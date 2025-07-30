from typing import Any

import numpy as np

from ._camera import CameraIntrinsics
from ._format_checks_internal import is_floating_array
from ._vec_len_map_internal import get_vec_len_map_mult_unchecked


def dist_map_2_depth_map(
    *, dist_map: np.ndarray, cam: CameraIntrinsics, verify_args: bool = False
) -> np.ndarray:
    """
    Convert one or more distance map to depth maps. This function does not use the depth mask, so it does not require it.

    Parameters
    ----------
    dist_map
        The distance map(s). Format: ``Ims_Dist`` or ``Im_Dist``
    cam
        The camera parameters.
    verify_args
        If this is true, then the function verifies the arguments and raises errors if the shapes or data types are incorrect. Otherwise the possible errors are treated as implementation detail.

    Returns
    -------
    v
        The depth map(s). Format: ``Ims_Dist`` or ``Im_Dist`` depending on ``dist_map``

    Raises
    ------
    ValueError
        If ``depth_map`` does not have format ``Ims_Dist`` or ``Im_Dist``.
    """
    if verify_args:
        _verify_map_conv_args(dist_map)

    vec_lens = get_vec_len_map_mult_unchecked(input_im=dist_map, d=1, cam=cam)

    return dist_map / vec_lens


def depth_map_2_dist_map(
    *, depth_map: np.ndarray, cam: CameraIntrinsics, verify_args: bool = False
) -> np.ndarray:
    """
    Convert one or more depth maps to distance maps. This function does not use the depth mask, so it does not require it.

    Parameters
    ----------
    depth_map
        The depth map(s). Format: ``Ims_Depth`` or ``Im_Depth``
    cam
        The camera parameters.
    verify_args
        If this is true, then the function verifies the arguments and raises errors if the shapes or data types are incorrect. Otherwise the possible errors are treated as implementation detail.

    Returns
    -------
    v
        The distance map(s). Format: ``Ims_Dist`` or ``Im_Dist`` depending on ``depth_map``

    Raises
    ------
    ValueError
        If ``depth_map`` does not have format ``Ims_Dist`` or ``Im_Dist``.
    """
    if verify_args:
        _verify_map_conv_args(depth_map)

    vec_lens = get_vec_len_map_mult_unchecked(input_im=depth_map, d=1, cam=cam)

    return depth_map * vec_lens


def _verify_map_conv_args(map: np.ndarray) -> None:
    """
    Raises
    ------
    ValueError
        If ``depth_map`` does not have format ``Ims_Dist`` or ``Im_Dist``.
    """
    if len(map.shape) not in [3, 4]:
        raise ValueError(
            f"The array containing the given map(s) should have 3 or 4 dimensions. Current shape: {map.shape}"
        )

    if map.shape[-3] != 1:
        raise ValueError(
            f"The array containing the given map(s) should have size 1 alongside dimension -3. Current shape: {map.shape}"
        )

    if not is_floating_array(map):
        raise ValueError(
            f"The array containing the given map(s) should contain floating point data. Current dtype: {map.shape}"
        )
