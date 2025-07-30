import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, cast, overload

import numpy as np
from typing_extensions import NotRequired, TypedDict

from ._camera import CameraIntrinsics
from ._coord_sys import CoordSys, get_coord_sys_conv_mat

if TYPE_CHECKING:
    import matplotlib.axes
    import mpl_toolkits.mplot3d
    import plotly.graph_objects as go

from ._logging_internal import LOGGER


class PointSubsamplingConf(TypedDict):
    rng: NotRequired[np.random.Generator]
    max_num: int


@overload
def depth_2_point_cloud(
    *,
    depth_map: np.ndarray,
    depth_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
    out_coord_sys: CoordSys,
    subsample_points: PointSubsamplingConf | None = None,
) -> np.ndarray:
    """
    Convert the given depth map to a point cloud.

    Parameters
    ----------
    depth_map
        The depth map to convert. Format: ``Depth_Im``
    mask
        The mask that selects the valid pixels on the depth map. Format: ``Im_Mask``
    intrinsics
        The intrinsics of the camera.

    Returns
    -------
    v
        The points of the generated point cloud. Format: ``3d_Points``

    Raises
    ------
    ValueError
        If the format of any of the arrays is incorrect.
    """
    ...


@overload
def depth_2_point_cloud(
    *,
    depth_map: np.ndarray,
    depth_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
    out_coord_sys: CoordSys,
    subsample_points: PointSubsamplingConf | None = None,
    image: None,
) -> np.ndarray:
    """
    Convert the given depth map to a point cloud.

    Parameters
    ----------
    depth_map
        The depth map to convert. Format: ``Depth_Im``
    mask
        The mask that selects the valid pixels on the depth map. Format: ``Im_Mask``
    intrinsics
        The intrinsics of the camera.
    image
        If the image is given, then it is converted to a format that maps a color for each returned point. Transfer function: consistent with the image. Format: ``RGB_Points``

    Returns
    -------
    v
        The points of the generated point cloud. Format: ``3d_Points``

    Raises
    ------
    ValueError
        If the format of any of the arrays is incorrect.
    """
    ...


@overload
def depth_2_point_cloud(
    *,
    depth_map: np.ndarray,
    depth_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
    out_coord_sys: CoordSys,
    image: np.ndarray,
    subsample_points: PointSubsamplingConf | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert the given depth map to a point cloud.

    Parameters
    ----------
    depth_map
        The depth map to convert. Format: ``Depth_Im``
    mask
        The mask that selects the valid pixels on the depth map. Format: ``Im_Mask``
    intrinsics
        The intrinsics of the camera.
    image
        If the image is given, then it is converted to a format that maps a color for each returned point. Transfer function: consistent with the image. Format: ``RGB_Points``

    Returns
    -------
    v
        A tuple ``(point_cloud, color_vectors)``. The element ``point_cloud`` contains the points of the generated point cloud (format: ``3d_Points``); the element ``color_vectors`` contains the corresponding color values (format: ``Color_Points``).

    Raises
    ------
    ValueError
        If the format of any of the arrays is incorrect.
    """
    ...


def depth_2_point_cloud(
    *,
    depth_map: np.ndarray,
    depth_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
    out_coord_sys: CoordSys,
    subsample_points: PointSubsamplingConf | None = None,
    image: np.ndarray | None = None,
):
    if len(depth_map.shape) != 3:
        raise ValueError(
            f'The array "depth_map" does not have format "Depth_Im", because it is not 3 dimensional. Shape: {depth_map.shape}'
        )

    if len(depth_mask.shape) != 3:
        raise ValueError(
            f'The array "depth_mask" does not have format "Im_Mask", because it is not 3 dimensional. Shape: {depth_mask.shape}'
        )

    if not np.issubdtype(depth_map.dtype, np.floating):
        raise ValueError(
            f'The array "depth_map" does not have format "Depth_Im", because its dtype is not floating. Dtype: {depth_map.dtype}'
        )

    if not np.issubdtype(depth_mask.dtype, np.bool_):
        raise ValueError(
            f'The array "depth_mask" does not have format "Im_Mask", because its dtype is not boolean. Dtype: {depth_mask.dtype}'
        )

    if depth_map.shape[0] != 1:
        raise RuntimeError(
            f'The array "depth_map" does not contain a depth map. Number of channels: {depth_map.shape[0]}.'
        )
    if depth_mask.shape[0] != 1:
        raise RuntimeError(
            f'The array "depth_mask" does not contain an image mask. Number of channels: {depth_mask.shape[0]}.'
        )

    if image is not None:
        if len(image.shape) != 3:
            raise ValueError(
                f'The array "image" does not have format "Im_RGB", because it is not 3 dimensional. Shape: {image.shape}'
            )
        if not np.issubdtype(image.dtype, np.floating):
            raise ValueError(
                f'The array "image" does not have format "Im_RGB", because its dtype is not floating. Dtype: {image.dtype}'
            )
        if image.shape[0] != 3:
            raise RuntimeError(
                f'The array "image" does not contain an RGB image. Number of channels: {image.shape[0]}.'
            )

        im_height = image.shape[1]
        im_width = image.shape[2]
        depth_height = depth_map.shape[1]
        depth_width = depth_map.shape[2]

        if (im_height, im_width) != (depth_height, depth_width):
            raise ValueError(
                f"The width and height of the image (width={im_width}, height={im_height}) does not equal to the width and height of the depth map (width={depth_width}, height={depth_height})."
            )

    height = depth_map.shape[-2]
    width = depth_map.shape[-1]
    px_x = np.arange(0.5, width, 1)
    px_y = np.arange(height - 0.5, 0, -1)

    px_x_im, px_y_im = np.meshgrid(px_x, px_y)

    px_x_im_flat = px_x_im.flatten(order="C")
    px_y_im_flat = px_y_im.flatten(order="C")
    depth_flat = depth_map.flatten(order="C")
    depth_mask_flat = depth_mask.flatten(order="C")

    px_x_im_flat = px_x_im_flat[depth_mask_flat]
    px_y_im_flat = px_y_im_flat[depth_mask_flat]
    depth_flat = depth_flat[depth_mask_flat]

    intrinsic_mat_inv = intrinsics.get_intrinsic_mat_inv()

    h_positions = np.stack(
        [px_x_im_flat * depth_flat, px_y_im_flat * depth_flat, depth_flat]
    )
    restored_positions = intrinsic_mat_inv @ h_positions

    coord_sys_conv_mat = get_coord_sys_conv_mat(from_=CoordSys.LH_YUp, to=out_coord_sys)
    restored_positions = coord_sys_conv_mat @ restored_positions

    restored_positions = restored_positions.T

    point_indexer = None
    if subsample_points is not None:
        if "rng" in subsample_points.keys():
            rng = subsample_points["rng"]  # type: ignore
        else:
            rng = np.random.default_rng()

        max_n_points = subsample_points["max_num"]
        if len(restored_positions) > max_n_points:
            point_indexer = rng.choice(
                len(restored_positions), max_n_points, replace=False
            )

    if point_indexer is not None:
        restored_positions = restored_positions[point_indexer]

    if image is not None:
        r: np.ndarray = image[0].flatten(order="C")
        g: np.ndarray = image[1].flatten(order="C")
        b: np.ndarray = image[2].flatten(order="C")

        r = r[depth_mask_flat]
        g = g[depth_mask_flat]
        b = b[depth_mask_flat]

        if point_indexer is not None:
            r = r[point_indexer]
            g = g[point_indexer]
            b = b[point_indexer]

        return restored_positions, np.stack([r, g, b], axis=-1)
    else:
        return restored_positions


def depths_2_matplotlib_fig(
    *,
    depth_maps: "Iterable[_DepthMapPresentConf]",
    intrinsics: CameraIntrinsics,
    coord_sys: CoordSys,
    subsample: PointSubsamplingConf | None = None,
    title: str | None = None,
    ax: "matplotlib.axes.Axes | None" = None,
) -> "mpl_toolkits.mplot3d.Axes3D":
    """
    Show the given depth maps on a Matplotlib point cloud figure.

    The displayed depth maps are contained by a collection. Each element is a mapping, with the following keys:

    * ``depth_map``: The depth map to dislay. Format: ``Im_Depth``
    * ``color``: The colors of the markers. It is either None, a string, or an RGB image that specifies the colof for each pixel individually. Format of the imgae: ``Im_RGB``
    * ``size``: The size of the markers. It is either None or a pisitive float.
    * ``name``: The legend for the depth map.

    The function shows a warning if a depth mask does not select any pixel.

    Extra dependencies: matplotlib

    Parameters
    ----------
    depth_maps
        A dict, where the keys denote the legends of the figures, the values contain the configurations of the displaying of the depth maps. The format of the depth maps: ``Depth_Im``
    intrinsics
        The intrinsics of the camera that captured the depth maps.
    coord_sys
        The coordinate system of the figure.
    ax
        The Matplotlib axis onto which the figure should be drawn. If not present, then the function creates a new subplot using ``plt.gcf().add_subplot(projection="3d")``

    Returns
    -------
    v
        The axes for the created subplot. The aspect mode is ``equal``

    Raises
    ------
    ValueError
        If any of the arrays have incorrect format.
    """
    # TODO test function

    # import the necessary modules
    import matplotlib.pyplot as plt
    import mpl_toolkits.mplot3d

    if ax is None:
        ax = plt.gcf().add_subplot(projection="3d")

    if ax.name != "3d":
        raise ValueError("A 3d axis should be used.")

    label_added = False

    for conf in depth_maps:
        if not conf["depth_mask"].any():
            im_name = conf["name"]
            LOGGER.warning(f'The mask for image "{im_name}" excludes all pixels.')

        if "name" in conf:
            label_added = True

        marker_size = conf.get("size", None)
        point_cloud_color_conf = conf.get("color", None)
        if point_cloud_color_conf is None:
            point_cloud = depth_2_point_cloud(
                depth_map=conf["depth_map"],
                depth_mask=conf["depth_mask"],
                intrinsics=intrinsics,
                out_coord_sys=coord_sys,
                subsample_points=subsample,
            )
            point_cloud_color: str | np.ndarray | None = None
        elif isinstance(point_cloud_color_conf, str):
            point_cloud = depth_2_point_cloud(
                depth_map=conf["depth_map"],
                depth_mask=conf["depth_mask"],
                intrinsics=intrinsics,
                out_coord_sys=coord_sys,
                subsample_points=subsample,
            )
            point_cloud_color = point_cloud_color_conf
        else:
            point_cloud, point_cloud_color = depth_2_point_cloud(
                depth_map=conf["depth_map"],
                depth_mask=conf["depth_mask"],
                intrinsics=intrinsics,
                image=point_cloud_color_conf,
                out_coord_sys=coord_sys,
                subsample_points=subsample,
            )

        if marker_size is None:
            ax.scatter(
                point_cloud[:, 0],
                point_cloud[:, 1],
                point_cloud[:, 2],
                color=point_cloud_color,
                label=conf["name"],
                alpha=conf.get("alpha", 1),
            )
        else:
            ax.scatter(
                point_cloud[:, 0],
                point_cloud[:, 1],
                point_cloud[:, 2],
                color=point_cloud_color,
                s=marker_size,  # type: ignore
                label=conf["name"],
                alpha=conf.get("alpha", 1),
            )

    # dicts that specify the handedness and up axis of the coordinate systems
    # TODO move this info to the enum
    is_y_up_dict = {
        CoordSys.LH_YUp: True,
        CoordSys.RH_YUp: True,
        CoordSys.LH_ZUp: False,
        CoordSys.RH_ZUp: False,
    }
    is_left_handed_dict = {
        CoordSys.LH_YUp: True,
        CoordSys.LH_ZUp: True,
        CoordSys.RH_YUp: False,
        CoordSys.RH_ZUp: False,
    }

    # make sure that the handedness is correct (matplotlib uses a right handed 3d coordinate system by default)
    ax.xaxis.set_inverted(is_left_handed_dict[coord_sys])
    ax.yaxis.set_inverted(False)
    cast(mpl_toolkits.mplot3d.Axes3D, ax).zaxis.set_inverted(False)

    # make sure that the up axis is properly coufigured
    # we also work around that the vertical axis label is not always visible
    # see (https://stackoverflow.com/questions/75275130/z-label-does-not-show-up-in-3d-matplotlib-scatter-plot)
    if is_y_up_dict[coord_sys]:
        cast(mpl_toolkits.mplot3d.Axes3D, ax).view_init(vertical_axis="y")
        ax.yaxis.labelpad = -0.7
    else:
        cast(mpl_toolkits.mplot3d.Axes3D, ax).view_init(vertical_axis="z")
        cast(mpl_toolkits.mplot3d.Axes3D, ax).zaxis.labelpad = -0.7

    # configure the aspect ratio
    ax.set_aspect("equal")

    # configure the title
    if title is not None:
        ax.set_title(title)

    # If no label is added, then ax.legend will
    # show a warning, so we do not call it in this case.
    if label_added:
        ax.legend()

    return cast(mpl_toolkits.mplot3d.Axes3D, ax)


def depths_2_plotly_fig(
    *,
    depth_maps: "Iterable[_DepthMapPresentConf]",
    intrinsics: CameraIntrinsics,
    coord_sys: CoordSys,
    subsample: PointSubsamplingConf | None = None,
    title: str | None = None,
) -> "go.Figure":
    """
    Show the given depth maps on a Plotly point cloud figure. This function needs Plotly to be installed.

    The displayed depth maps are contained by a collection. Each element is a mapping, with the following keys:

    * ``depth_map``: The depth map to dislay. Format: ``Im_Depth``
    * ``color``: The colors of the markers. It is either None, a string, or an RGB image that specifies the colof for each pixel individually. Format of the imgae: ``Im_RGB``
    * ``size``: The size of the markers. It is either None or a pisitive float.
    * ``name``: The legend for the depth map.

    The function shows a warning if a depth mask does not select any pixel.

    Extra dependencies: plotly

    Parameters
    ----------
    depth_maps
        A dict, where the keys denote the legends of the figures, the values contain the configurations of the displaying of the depth maps. The format of the depth maps: ``Depth_Im``
    intrinsics
        The intrinsics of the camera that captured the depth maps.
    coord_sys
        The coordinate system of the figure.

    Raises
    ------
    ValueError
        If any of the arrays have incorrect format.

    Developer notes
    ---------------
    The camera matrix is controlled by two properties in Plotly.

    * The camera controls (described at <https://plotly.com/python/3d-camera-controls/>) describe the position and rotation of the camera.
    * The potential mirroring of the data is described by the axes (described at <https://plotly.com/python/3d-axes/>).

    By default, Plotly uses a Z-up left-handed coordinate system.

    The camera controls are:

    * ``eye``: The initial position of the camera. The camera looks at the center.
    * ``up``: Gives the up-vector for the look-at matrix of the camera. This tilts the camera.
    * ``center``: Move the point around which the camera rotates. If it is ``{"x": 0, "y": 0, "z": 0}`` (default), then the camera is rotated around the center of the area.

    The axes are mirrored by setting the corresponding autorange (``xaxis_autorange``, ``yaxis_autorange``, ``zaxis_autorange``) to ``reversed``.

    We configure the diagram using the following rules:

    * Set ``xaxis_autorange`` to ``reversed`` if we have a right-handed coordinate system. Otherwise we do not specify it.
    * Set camera ``up`` to ``{"x": 0, "y": 0, "z": 1}`` if we have a Z-up coordinate system, otherwise we configure it to be ``{"x": 0, "y": 1, "z": 0}``.
    * The camera position is set to ``{"x": 1.25, "y": 1.25, "z": 1.25}``, regardless of the coordinate system.
    * The camera rotation center is set to ``{"x": 0, "y": 0, "z": 0}``, regardless of the coordinate system.
    * The ``yaxis_autorange``, ``zaxis_autorange`` scene properties are kept unset.

    The aspect mode of the figure is ``data``.
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise RuntimeError(
            "The installation of the optional dependency, Plotly is required to create Plotly figures."
        )

    # how to tilt the camera by the up-direction
    cam_up_by_coord_sys = {
        CoordSys.LH_YUp: {"x": 0, "y": 1, "z": 0},
        CoordSys.RH_YUp: {"x": 0, "y": 1, "z": 0},
        CoordSys.LH_ZUp: {"x": 0, "y": 0, "z": 1},
        CoordSys.RH_ZUp: {"x": 0, "y": 0, "z": 1},
    }

    # how to flip the X-axis by the handedness
    reverse_x_by_coord_sys = {
        CoordSys.LH_YUp: True,
        CoordSys.LH_ZUp: True,
        CoordSys.RH_YUp: False,
        CoordSys.RH_ZUp: False,
    }

    # calculate the total camera position and rotation
    scene_camera = {
        "eye": {"x": 1.25, "y": 1.25, "z": 1.25},
        "up": cam_up_by_coord_sys[coord_sys],
        "center": {"x": 0, "y": 0, "z": 0},
    }

    reverse_x = reverse_x_by_coord_sys[coord_sys]

    fig = go.Figure()
    for conf in depth_maps:
        if not conf["depth_mask"].any():
            im_name = conf["name"]
            LOGGER.warning(f'The mask for image "{im_name}" excludes all pixels.')

        marker_size = conf.get("size", None)
        point_cloud_color_conf = conf.get("color", None)
        if point_cloud_color_conf is None:
            point_cloud = depth_2_point_cloud(
                depth_map=conf["depth_map"],
                depth_mask=conf["depth_mask"],
                intrinsics=intrinsics,
                out_coord_sys=coord_sys,
                subsample_points=subsample,
            )
            point_cloud_color: str | np.ndarray | None = None
        elif isinstance(point_cloud_color_conf, str):
            point_cloud = depth_2_point_cloud(
                depth_map=conf["depth_map"],
                depth_mask=conf["depth_mask"],
                intrinsics=intrinsics,
                out_coord_sys=coord_sys,
                subsample_points=subsample,
            )
            point_cloud_color = point_cloud_color_conf
        else:
            point_cloud, point_cloud_color = depth_2_point_cloud(
                depth_map=conf["depth_map"],
                depth_mask=conf["depth_mask"],
                intrinsics=intrinsics,
                image=point_cloud_color_conf,
                out_coord_sys=coord_sys,
                subsample_points=subsample,
            )

        trace = go.Scatter3d(
            x=point_cloud[:, 0],
            y=point_cloud[:, 1],
            z=point_cloud[:, 2],
            mode="markers",
            marker={"size": marker_size, "color": point_cloud_color},
            name=conf["name"],
            showlegend=True,
            opacity=conf.get("alpha", 1),
        )
        fig.add_trace(trace)

    # TODO test opacity

    if title is not None:
        fig.update_layout(title=title)

    if reverse_x:
        fig.update_scenes(xaxis_autorange="reversed")

    fig.update_scenes(aspectmode="data")

    fig.update_layout(scene_camera=scene_camera)

    return fig


class _DepthMapPresentConf(TypedDict):
    depth_map: np.ndarray
    depth_mask: np.ndarray
    color: NotRequired[np.ndarray | str | None]
    size: NotRequired[int | None]
    name: str
    alpha: NotRequired[float]
