from typing import Final

import numpy as np


class DepthClip:
    """
    This class implements the operations for depth clipping for both the predictions and the depth masks.

    The application on the mask simulates sensors with limited range.

    Parameters
    ----------
    clip_range
        The ``(minimal_depth, maximal_depth)`` tuple, if present. Otherwise no clipping is applied.

    Raises
    ------
    ValueError
        If ``minimal_depth >= maximal_depth``
    """

    def __init__(self, clip_range: tuple[float, float] | None) -> None:
        if clip_range is not None:
            if clip_range[0] >= clip_range[1]:
                raise ValueError(
                    f"The minimal value of the depth clip ({clip_range[0]}) is not less than the maximal value ({clip_range[1]})."
                )

        self._clip_range: Final = clip_range

    @property
    def clip_range(self) -> tuple[float, float] | None:
        return self._clip_range

    def on_aligned_pred(
        self, aligned_preds: np.ndarray, verify_args: bool = False
    ) -> np.ndarray:
        """
        Applies the clipping operation on the depth predictions.

        It sets the minimum depth for the nan values and the maximum depth from the infinity values. For other values, the following formula applies: ``np.clip(aligned_preds, min_depth, max_depth)``.

        If the depth alignemnt depends on the ground truth, then it is the caller's responsibility to decide if the alignment should be based on the ground truths with the post-clip masks (created with `DepthClip.on_mask`) or not.

        Parameters
        -----------
        aligned_preds
            The aligned depth predictions. Format: ``SingleArray_Scalar``
        verify_args
            If true, then the function checks the array dtype.

        Returns
        -------
        v
            The clipped aligned depths. Format: ``SingleArray_Scalar``

        Raises
        ------
        ValueError
            If the argument verification is enabled and the depth array does not have the correct dtype.
        """
        if verify_args:
            if not np.issubdtype(aligned_preds.dtype, np.floating):
                raise ValueError(
                    f"The array containing the depth data should contain floating point numbers (np.floating). Current dtype: {aligned_preds.dtype}"
                )

        if self.clip_range is not None:
            aligned_preds[np.isinf(aligned_preds)] = self.clip_range[1]
            aligned_preds[np.isnan(aligned_preds)] = self.clip_range[0]
            return np.clip(aligned_preds, self.clip_range[0], self.clip_range[1])
        else:
            return aligned_preds

    def on_mask(
        self, *, gt_depth: np.ndarray, mask: np.ndarray, verify_args: bool = False
    ) -> np.ndarray:
        """
        Modifies the ground truth mask to reject the pixels containing values outside of the range. It follows the following rules:

        * If the mask is boolean, then sets the pixels to reject to false.
        * If the mask is floating, then multiplies the pixels to reject by 0.

        Parameters
        ----------
        gt_depth
            The ground truth depth values. Format: Format: ``SingleArray_Scalar``
        mask
            The ground truth mask. Format: ``SingleArray_Mask`` and its shape should be the same as ``gt_depth``

        Raises
        ------
        ValueError
            If the argument verification is enabled and any of the arrays do not have the correct dtype or the shape of the arrays do not match.
        """
        if verify_args:
            if not np.issubdtype(gt_depth.dtype, np.floating):
                raise ValueError(
                    f"The depth array does not have floating data type. Actual dtype: {mask.dtype}"
                )
            if not (
                np.issubdtype(mask.dtype, np.bool_)
                or np.issubdtype(mask.dtype, np.floating)
            ):
                raise ValueError(
                    f"The mask does not have boolean or floating dtype. Actual dtype: {mask.dtype}"
                )
            if mask.shape != gt_depth.shape:
                raise ValueError(
                    f"The shape of the mask ({mask.shape}) and the shape of the ground truth depths ({gt_depth.shape}) do not match."
                )

        if self.clip_range is not None:
            if np.issubdtype(mask.dtype, np.bool_):
                return (
                    mask
                    & (gt_depth < self.clip_range[1])
                    & (gt_depth > self.clip_range[0])
                )
            else:
                extra_selector = (gt_depth > self.clip_range[1]) & (
                    gt_depth < self.clip_range[0]
                )
                return mask * extra_selector.astype(mask.dtype)
        else:
            return mask

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"DepthClip({self.clip_range})"
