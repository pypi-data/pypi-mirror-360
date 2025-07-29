import torch

from .._depth_clip import DepthClip


def depth_clip_on_aligned_pred(
    *, clip: DepthClip, aligned_preds: torch.Tensor, verify_args: bool = False
) -> torch.Tensor:
    """
    Applies the clipping operation on the depth predictions.

    It sets the minimum depth for the nan values and the maximum depth from the infinity values. For other values, the following formula applies: ``np.clip(aligned_preds, min_depth, max_depth)``.

    If the depth alignemnt depends on the ground truth, then it is the caller's responsibility to decide if the alignment should be based on the ground truths with the post-clip masks (created with `DepthClip.on_mask`) or not.

    Parameters
    -----------
    aligned_preds
        The aligned depth predictions. Format: any floating point array that contaisn depth values
    verify_args
        If true, then the function checks the array dtype.

    Returns
    -------
    v
        The clipped aligned depths. Format: any array

    Raises
    ------
    ValueError
        If the argument verification is enabled and the depth array does not have the correct dtype.
    """
    if verify_args:
        if not aligned_preds.is_floating_point():
            raise ValueError(
                f"The array containing the depth data should contain floating point numbers (np.floating). Current dtype: {aligned_preds.dtype}"
            )

    if clip.clip_range is not None:
        aligned_preds[torch.isinf(aligned_preds)] = clip.clip_range[1]
        aligned_preds[torch.isnan(aligned_preds)] = clip.clip_range[0]
        return torch.clip(aligned_preds, clip.clip_range[0], clip.clip_range[1])
    else:
        return aligned_preds


def depth_clip_on_mask(
    clip: DepthClip,
    *,
    gt_depth: torch.Tensor,
    mask: torch.Tensor,
    verify_args: bool = False,
) -> torch.Tensor:
    """
    Modifies the ground truth mask to reject the pixels containing values outside of the range. It follows the following rules:

    * If the mask is boolean, then sets the pixels to reject to false.
    * If the mask is floating, then multiplies the pixels to reject by 0.

    Parameters
    ----------
    gt_depth
        The ground truth depth values. Format: any floating point array that contaisn depth values
    mask
        The ground truth mask. Format: any boolean of floating array with shape equal to ``gt_depth``
    """
    if verify_args:
        if not gt_depth.is_floating_point():
            raise ValueError(
                f"The depth array does not have floating data type. Actual dtype: {mask.dtype}"
            )
        if not ((mask.dtype == torch.bool) or mask.is_floating_point()):
            raise ValueError(
                f"The mask does not have boolean or floating dtype. Actual dtype: {mask.dtype}"
            )
        if mask.shape != gt_depth.shape:
            raise ValueError(
                f"The shape of the mask ({mask.shape}) and the shape of the ground truth depths ({gt_depth.shape}) do not match."
            )

    if clip.clip_range is not None:
        if mask.dtype == torch.bool:
            return (
                mask & (gt_depth < clip.clip_range[1]) & (gt_depth > clip.clip_range[0])
            )
        else:
            extra_selector = (gt_depth > clip.clip_range[1]) & (
                gt_depth < clip.clip_range[0]
            )
            return mask * extra_selector.to(mask.dtype)
    else:
        return mask
