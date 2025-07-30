import datetime
import logging
from typing import TypedDict

import numpy as np
from typing_extensions import NotRequired

from ._camera import CameraIntrinsics
from ._coord_sys import CoordSys, get_coord_sys_conv_mat
from ._point_cloud import PointSubsamplingConf, depth_2_point_cloud


def fast_dilate_depth_map(
    depth_map: np.ndarray,
    depth_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
    r: float,
    occlusion_subsampling: "PointSubsamplingConf|None" = None,
) -> np.ndarray:
    """
    Implement a fast dilation-like operation on the depth maps.

    The function tries to estimate effect of the depth map formed by points that have a given distance from the points of the depth map. Ideally, this would mean that we draw as sphere around each point, with a given radius. However, this would be quite slow. So, we approximate this using the following effect:

    - Calculate the "dilate-like" depth map as if there was no occlusion.
    - Draw the front faces of the axis-aligned bounding box around a given number of points to fake occlusion. If these front faces would not be in front of the camera, then the same faces are drawn a the center of the cube instead. To make everything even quicker, the function can also be configured to only draw these bounding boxes around a randomly sampled subset of points.

    The function returns with constant 0-s if there are no selected pixels on the depth map. If there is a point in the depth map that is closer to the camera than r, then the function returns with constant 0-s, since in this case, the camera is INSIDE of the resulting dilated object.

    If ``r=0``, the function returns with a copy of the depth map where the non-selected values are set to 0.

    Parameters
    ----------
    depth_map
        The depth map on which the dilation is applied. Format: ``Im_Depth``
    depth_mask
        The mask for the depth map. Format: ``Im_Mask``
    intrinsics
        The camera intrinsics.
    r
        The radius of the approximated sphere.
    occlusion_subsampling
        How to subsample the points to draw the AABB front faces that simulate the occlusion. If this is None, then the points are not subsampled. If the number of points to subsample is 0, then the occlusion is not simulated at all.

    Return
    ------
    v
        The resulting depth map. Format: ``Im_Depth``

    Raises
    ------
    ValueError
        If any of the arrays does not have the proper format.

        If the radius is negative.

    Notes
    -----
    The dilation is not supported for depth maps that contain selected values less than the radius of the approximated spheres. Reason: this greatly simplifies the implementation.
    """
    if r < 0:
        raise ValueError(f"The radius of the approximated sphere ({r}) is negative.")

    if not np.issubdtype(depth_map.dtype, np.floating):
        raise ValueError(
            f"The depth map does not have format Im_Depth. The dtype is not floating. Dtype: {depth_map.dtype}"
        )
    if (len(depth_map.shape) != 3) or (depth_map.shape[0] != 1):
        raise ValueError(
            f"The depth map does not have format Im_Depth. It does not have exactly 3 dimensions or its dimension 0 does not have length 1. Shape: {depth_map.shape}"
        )
    if not np.issubdtype(depth_mask.dtype, np.bool_):
        raise ValueError(
            f"The depth mask does not have format Im_Mask. The dtype is not bool. Dtype: {depth_mask.dtype}"
        )
    if depth_mask.shape != depth_map.shape:
        raise ValueError(
            f"The shape of the depth map ({depth_map.shape}) is not equal to the shape of the depth mask ({depth_mask.shape})."
        )

    # if there are no selected pixels on the depth map,
    # then we return with a depth map containing all zeros
    if not np.any(depth_mask):
        return np.zeros_like(depth_map)

    if r == 0.0:
        depth_map_copy = depth_map.copy()
        depth_map_copy[~depth_mask] = 0
        return depth_map_copy

    # convert the depth map to a view-space position map
    vs_map = _get_vs_map_lh_yup_unchecked(
        depth_map=depth_map, depth_mask=depth_mask, intrinsics=intrinsics
    )

    # if we are in an object, then we should return with constant 0-s
    if _is_any_point_not_farther_unchecked(
        vs_map=vs_map, depth_mask=depth_mask, d_min=r
    ):
        return np.zeros_like(depth_map)

    # calculate the constant that approximates the effect of dilation without occulusion (i. e. drawing a sphere without anything that blocks it)
    dz_map = _get_sphere_dz_map_unchecked(
        valid_points_mask=depth_mask, r=r, vs_map=vs_map
    )

    # if the occlusion is not considered, then we can just return with the Z coordinates that would occur without occlusion
    if occlusion_subsampling is not None:
        if occlusion_subsampling["max_num"] == 0:
            return depth_map + dz_map

    # create the point cloud from the view-space position map
    point_cloud = np.stack(
        [
            vs_map[0][depth_mask[0]].flatten(),
            vs_map[1][depth_mask[0]].flatten(),
            vs_map[2][depth_mask[0]].flatten(),
        ],
        axis=-1,
    )

    # subsampling
    if occlusion_subsampling is not None:
        rng = occlusion_subsampling.get("rng")
        if rng is None:
            rng = np.random.default_rng()

        indices = rng.choice(
            len(point_cloud),
            size=min(occlusion_subsampling["max_num"], len(point_cloud)),
            replace=False,
        )
        point_cloud = point_cloud[indices]

    # draw the cubes
    result = _draw_axis_aligned_cube_front_faces_lh_yup_unchecked(
        depth_map=depth_map,
        cube_centers_vs=point_cloud,
        r=r,
        intrinsics=intrinsics,
        depth_mask=depth_mask,
        depth_const_add=dz_map,
    )

    # return with the reesult
    return result


def _is_any_point_not_farther_unchecked(
    vs_map: np.ndarray, depth_mask: np.ndarray, d_min: float
) -> bool:
    """
    Checks if a point is farther than the given minimal distance.

    Parameters
    ----------
    vs_map
        The map containing the points. Format: ``Im_VS``
    depth_mask
        The mask that selects the valid pixels in the map.
    d_min
        The minimal distance.

    Returns
    -------
    v
        True if at least one such point exsits. Otherwise False.
    """
    distance_map = np.linalg.norm(vs_map, axis=0, ord=2, keepdims=True)
    return bool(np.any(distance_map[depth_mask] <= d_min))


def _get_sphere_dz_map_unchecked(
    vs_map: np.ndarray, valid_points_mask: np.ndarray, r: float
) -> np.ndarray:
    """
    Take a point p in view space. The view space an Y-up left handed coordinate system, where the camera looks at the +Z direction. Assume that we calculate the intersection of the sphere around p, with radius r, and the ray from the camera to p. Let be the z coordinate of p ``z_p`` and the z-coordinate of the intersection ``z_i``. This function returns with ``dz=z_i-z_p``.

    This function does not check its parameters.

    Parameters
    ----------
    vs_map
        A map that denotes the view space position of the point for each pixel. Format: ``Im_VS``
    valid_points_mask
        The mask that selects the valid pixels in the view space position map. Format: ``Im_Mask``
    r
        The radius of the sphere.

    Returns
    -------
    v
        The ``dz=i_p-z_p`` value for each valid pixel; 0 for the other pixels. Format: ``Im_Scalar``
    """
    # dz = -1*normalize(vs_pos).z*r
    vs_len_map = np.linalg.norm(vs_map, ord=2, axis=0, keepdims=True)
    dz_map = vs_map[[-1]].copy()
    dz_map[valid_points_mask] = (
        -dz_map[valid_points_mask] / vs_len_map[valid_points_mask]
    )
    dz_map[valid_points_mask] = dz_map[valid_points_mask] * r
    dz_map[~valid_points_mask] = 0
    return dz_map


def _get_vs_map_lh_yup_unchecked(
    *,
    depth_map: np.ndarray,
    depth_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
) -> np.ndarray:
    """
    Get the view-space position map for each pixel in a left-handed Y-up coordinate system.

    This function does not check its arguments.

    Parameters
    ----------
    depth_map
        The depth map. Format: ``Im_VS``
    depth_mask
        The mask that selects the valid pixels on the depth map. Format: ``Im_Mask``
    intrinsics
        The camera intrinsics.

    Returns
    -------
    v
        The view-space position map. Format: ``Im_VS``
    """

    _, height, width = depth_map.shape

    x_p, y_p = np.meshgrid(
        np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)[::-1]
    )

    m = depth_mask[0]

    result = np.zeros((3, height, width), dtype=depth_map.dtype)

    result[0][m] = (x_p[m] - intrinsics.c_x) * depth_map[0][m] / intrinsics.f_x
    result[1][m] = (y_p[m] - intrinsics.c_y) * depth_map[0][m] / intrinsics.f_y
    result[[2]] = depth_map

    return result


def _draw_axis_aligned_cube_front_faces_lh_yup_unchecked(
    depth_map: np.ndarray,
    depth_mask: np.ndarray,
    intrinsics: CameraIntrinsics,
    r: float,
    cube_centers_vs: np.ndarray,
    depth_const_add: np.ndarray,
) -> np.ndarray:
    """
    Draw cube front faces onto a depth map.

    The function does not draw the faces with negative depth.

    Unlike the public functions of this package, this function strictly assumes an Y-up left handed coordinate system, where the camera looks at the +Z direction.

    The function does not check its arguments.

    Parameters
    ----------
    depth_map
        The depth map onto which the cube faces should be drawn. Format: ``Im_Depth``
    intrinsics
        The camera properties.
    r
        The distance between the centers of the cubes and the centers of the corresponding front faces.
    cube_front_face_centers
        The centers of the front faces of the cubes to draw. The Z-coordinate should be positive. Format: ``Points_3D``
    background_dz
        A pixelwise constant that should be added to the depth map (it might be negative too). Format: ``Im_Scalar``

    Returns
    -------
    v
        The depth map with the cubes drawn. Format: ``Im_Depth``
    """
    _, height, width = depth_map.shape

    # calculate the centers of the front faces
    cube_front_face_centers_vs = cube_centers_vs.copy()
    cube_front_face_centers_vs[:, -1] -= r

    # reject all cubes that would go behind the camera
    cube_front_face_centers_vs = cube_front_face_centers_vs[
        cube_front_face_centers_vs[:, -1] > 0
    ]

    # sort the points with the following order:
    # 0. the point with the largest z-coordinate
    # last. The point with the smallest z-coordinate
    point_order = np.argsort(cube_front_face_centers_vs[:, 2])[::-1]

    # calculate the centers of the front faces of the squares
    reprojected_cube_centers = (
        intrinsics.get_intrinsic_mat() @ cube_front_face_centers_vs.T
    ).T

    reprojected_cube_centers = (
        reprojected_cube_centers / reprojected_cube_centers[:, [-1]]
    )
    reprojected_cube_centers = reprojected_cube_centers[:, [0, 1]]

    # flip the Y-cordinate, since we will use indices
    cube_front_face_center_idxs = np.stack(
        [reprojected_cube_centers[:, 0], height - reprojected_cube_centers[:, 1]],
        axis=1,
    )

    # calculate the sizes of the box front faces on the image
    proj_edg_half_lens_x = r * intrinsics.f_x / cube_front_face_centers_vs[:, 2]
    proj_edg_half_lens_y = r * intrinsics.f_y / cube_front_face_centers_vs[:, 2]

    # make sure that the drawing is not out of bounds
    # top left corners
    top_left_xs = np.clip(
        cube_front_face_center_idxs[:, 0] - proj_edg_half_lens_x, 0, width
    ).astype(np.int32)
    top_left_ys = np.clip(
        cube_front_face_center_idxs[:, 1] - proj_edg_half_lens_y, 0, height
    ).astype(np.int32)

    # bottom right corners
    bottom_right_xs = np.clip(
        cube_front_face_center_idxs[:, 0] + 1 + proj_edg_half_lens_x, 0, width
    ).astype(np.int32)
    bottom_right_ys = np.clip(
        cube_front_face_center_idxs[:, 1] + 1 + proj_edg_half_lens_y, 0, height
    ).astype(np.int32)

    # calculate the baseline z changes that do not consider occlusion
    depth_const_add = depth_const_add.copy()
    depth_const_add[~depth_mask] = 0

    # calculate the baseline depth map
    baseline_depth: np.ndarray = depth_map + depth_const_add

    # initialize the results buffer based on the initial depth map
    result: np.ndarray = baseline_depth.copy()

    # write the values
    for i in range(len(cube_front_face_centers_vs)):
        cube_idx = point_order[i]
        result[
            :,
            slice(top_left_ys[cube_idx], bottom_right_ys[cube_idx]),
            slice(top_left_xs[cube_idx], bottom_right_xs[cube_idx]),
        ] = cube_front_face_centers_vs[cube_idx, 2]

    # plt.imshow(result[0])
    # plt.show(block=True)
    # plt.close()

    # fix drawn cube front faces occluding depth values smaller than them
    result = np.minimum(baseline_depth, result)

    # write 0 to the pixels rejected by the original depth mask
    result[~depth_mask] = 0

    return result


def _reproject_points_unchecked(
    intrinsics: CameraIntrinsics, points_vs: np.ndarray
) -> np.ndarray:
    """
    Calculate the on-image pos
    """

    return np.stack(
        [
            (points_vs[:, 0] * intrinsics.f_x + points_vs[:, 2] * intrinsics.c_x)
            / points_vs[:, 2],
            (points_vs[:, 1] * intrinsics.f_y + points_vs[:, 2] * intrinsics.c_y)
            / points_vs[:, 2],
        ]
    )

    return new_x_proj_vals, new_y_proj_vals
