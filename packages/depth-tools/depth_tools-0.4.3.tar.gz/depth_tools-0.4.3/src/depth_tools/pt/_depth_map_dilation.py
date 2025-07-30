import torch


def is_dilation_supported(
    depth: torch.Tensor, depth_mask: torch.Tensor, r: float
) -> bool:
    """
    Checks if the dilation operation is supported on any depth map that contains the given depth values.

    The dilation is supported if all depth values selected by the depth mask are GREATER THAN r.

    Parameters
    ----------
    depth
        The depth values. Format: dtype: any floating point; shape: does not matter
    depth_mask
        A mask that selects the valid depth values. Format: dtype: any boolean; shape: same as the array of depth values
    r
        Same as the corresponding dilation parameter.

    Returns
    -------
    v
        True if the dilation is safe on any depth map with these depth values. Otherwise false.

    Raises
    ------
    ValueError
        If the shape of the depth mask and the depth value array does not match.

        If the depth array or the mask does not have the correct dtype.

        If r<0.
    """
    if depth.shape != depth_mask.shape:
        raise ValueError(
            f"The shape of the array containing the depth values ({depth.shape}) is not equal to the shape of the shape of the mask that selects the valid depth values ({depth_mask})."
        )

    if not depth.is_floating_point():
        raise ValueError(
            f"The array of depth values does not contain floating point data. Dtype: {depth.dtype}"
        )
    if depth_mask.dtype != torch.bool:
        raise ValueError(
            f"The array that contains the mask that selects the valid depth values does not contain boolean data. Dtype: {depth_mask.dtype}"
        )

    if r < 0:
        raise ValueError(f"The dilation radius ({r}) is negative.")

    return bool(torch.all(depth[depth_mask] > r))
