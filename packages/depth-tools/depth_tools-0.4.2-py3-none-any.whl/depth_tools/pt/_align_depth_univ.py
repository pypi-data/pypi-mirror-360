# The file is automatically generated from src\depth_tools\_align_depth_univ.py; do not edit.
import math
from collections.abc import Sequence
from typing import Any, SupportsIndex

import torch

from ._diverging_functions_internal import new_full
from ._format_checks_internal import is_bool_array, is_floating_array
from .._logging_internal import LOGGER


def align_shift_scale(
    *,
    pred_values: torch.Tensor,
    gt_values: torch.Tensor,
    mask: torch.Tensor,
    control_mask: torch.Tensor | None = None,
    verify_args: bool = False,
    first_dim_separates: bool = False,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Align the predicted scalar values to a ground truth scalar values with a shift and scale to minimize the MSE loss. This is can be used for disparity maps or depth maps produced by depth estimators that only estimate relative depth or metric depth estimators, when some ground truth depth is available during inference time. Note that some authors apply further pre-processing.

    The function assumes without checking that ``control_mask`` only selects a subset of the values of ``mask``, regardless of ``verify_args``.

    Parameters
    ----------
    pred_values
        The predicted scalar values. Format: a floating point array. If ``first_dim_separates``, then it should at least two dimensions.
    gt_values
        The ground truth scalar values. Format: a floating point array. If ``first_dim_separates``, then it should at least two dimensions. It should have the same shape and dtype as ``pred_values``
    mask
        The mask that selects the valid values. It should have the same width and height as the predicted scalar array. Format: ``SingleArray_Mask``. Format: a boolean array. If ``first_dim_separates``, then it should at least two dimensions. It should have the same shape as ``pred_values``
    control_mask
        An optional mask that selects the values used to calculate the shift and scale. If not specified, then all valid values will be used. If defined, it should have the same width and height as the predicted scalar array.  Format: a boolean array. If ``first_dim_separates``, then it should at least two dimensions. It should have the same shape as ``pred_values``
    first_dim_separates
        If true, then the alignment is done for each element of dimension 0 independently.

    Returns
    -------
    scaled_pred
        The scaled predictions. NaN if no value is selected to control the alignment. The aligned predictions.
    shift
        The shift applied. NaN if no value is selected to control the alignment.
    scale
        The scale applied. NaN if no value is selected to control the alignment.

    Raises
    ------
    ValueError
        If any of the checked parameter assumptions does not hold and ``verify_args=True``. Otherwise implementation detail.

    Notes
    -----
    This function intentionally implements only the bare bones of prediction alignment. We found that the fine details, not implemented by this function, are highly different between papers. For example, many papers (e.g. MiDAS papers) do the alignment in the disparity space. However, the depth -> disparity conversion is model-dependent.

    Developer notes
    ---------------
    The predicted and ground truth arrays should have the same dtype, because `torch.linalg.lstsq` has a similar requirement. Contrary, the similar Numpy function supports different dtypes for the arguments. However, we decided not to support this for Numpy, because this makes the Pytorch and Numpy implementations of these two functions consistent. This decision might be revisited later.
    """
    if control_mask is None:
        control_mask = mask

    if verify_args:
        _verify_align_shift_and_scale_map_args(
            pred_values, gt_values, mask, control_mask, first_dim_separates
        )

    if not first_dim_separates:
        return _apply_align_shift_scale_global_unchecked(
            pred_values=pred_values,
            gt_values=gt_values,
            control_mask=control_mask,
            mask=mask,
        )
    else:
        n_samples = pred_values.shape[0]
        pred_res_list: list[torch.Tensor] = []
        scales = torch.zeros(n_samples, dtype=pred_values.dtype)
        shifts = torch.zeros(n_samples, dtype=pred_values.dtype)

        for i in range(n_samples):
            p, shi, sca = _apply_align_shift_scale_global_unchecked(
                pred_values=pred_values[i],
                gt_values=gt_values[i],
                control_mask=control_mask[i],
                mask=mask[i],
            )

            pred_res_list.append(p)
            scales[i] = sca
            shifts[i] = shi

        pred_res = torch.stack(pred_res_list)

        return pred_res, shifts, scales


def _apply_align_shift_scale_global_unchecked(
    pred_values: torch.Tensor,
    gt_values: torch.Tensor,
    mask: torch.Tensor,
    control_mask: torch.Tensor | None = None,
) -> tuple[torch.Tensor, Any, Any]:
    """
    Implements the global alignment calculation. It has the same parameters as `align_shift_scale`.
    """
    pred_values_control = pred_values[control_mask]
    gt_values_control = gt_values[control_mask]
    if len(gt_values_control) == 0:
        LOGGER.warning(
            f"The prediction aligment failed, because the control mask (or the mask) does not select any value. Returning with nan."
        )
        return (
            new_full(gt_values, torch.nan, shape=pred_values.shape),
            new_full(gt_values, torch.nan, shape=(len(pred_values),)),
            new_full(gt_values, torch.nan, shape=(len(pred_values),)),
        )

    A = torch.stack([pred_values_control, torch.ones_like(pred_values_control)], dim=1)
    b = gt_values_control

    scale, shift = torch.linalg.lstsq(A, b)[0]

    scaled_pred = torch.zeros_like(pred_values)
    scaled_pred[mask] = pred_values[mask] * scale + shift
    scaled_pred[~mask] = 0
    return (
        scaled_pred,
        shift,
        scale,
    )


def _verify_align_shift_and_scale_map_args(
    pred_values: torch.Tensor,
    gt_values: torch.Tensor,
    mask: torch.Tensor,
    control_mask: torch.Tensor,
    first_dim_separates: bool,
) -> None:
    """
    Check if the parameters of `align_shift_scale` are consistent with the assumptions.

    Raises
    ------
    ValueError
        If any of the checked parameter assumptions does not hold.
    """
    if not is_floating_array(pred_values):
        raise ValueError(
            f"The array containing the predicted scalar map does not have format `Im_Scalar` it does not have floating dtype. Dtype: {pred_values.dtype}"
        )
    if not is_floating_array(gt_values):
        raise ValueError(
            f"The array containing the ground truth scalar map does not have format `Im_Scalar` it does not have floating dtype. Dtype: {pred_values.dtype}"
        )
    if not is_bool_array(mask):
        raise ValueError(
            f"The array containing the mask does not have format `Im_Mask` it does not have boolean dtype. Dtype: {pred_values.dtype}"
        )
    if not is_bool_array(control_mask):
        raise ValueError(
            f"The array containing the control mask does not have format `Im_Mask` it does not have boolean dtype. Dtype: {control_mask.dtype}"
        )
    if pred_values.dtype != gt_values.dtype:
        raise ValueError(
            f"The predicted and ground truth scalar maps should have the same dtype. Dtypes: predicted map: {pred_values.dtype}; ground truth map: {gt_values.dtype}"
        )

    all_other_maps = [gt_values, mask, control_mask]
    all_other_map_names = ["ground truth map", "mask", "control mask"]
    expected_shape = pred_values.shape

    for other_map, other_map_name in zip(all_other_maps, all_other_map_names):
        if other_map.shape != expected_shape:
            raise ValueError(
                f"The shape of the predicted scalar array is not equal to the shape of {other_map_name}. Shape of the {other_map_name}: {other_map.shape}; Shape of the predicted map: {pred_values.shape}"
            )

    if first_dim_separates and (len(pred_values.shape) < 2):
        raise ValueError(
            f"If first_dim_separates=True, then the array of predicted values should have at least two dimensions. Current shape: {tuple(pred_values.shape)}"
        )
