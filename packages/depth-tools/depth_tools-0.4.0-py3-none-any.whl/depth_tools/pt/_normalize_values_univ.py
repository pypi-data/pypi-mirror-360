# The file is automatically generated from src\depth_tools\_normalize_values_univ.py; do not edit.
import torch

from ._diverging_functions_internal import nanmean, nanmedian
from ._format_checks_internal import is_bool_array, is_dim_sel_ok, is_floating_array


def normalize_values(
    *,
    values: torch.Tensor,
    mask: torch.Tensor,
    first_dim_separates: bool = False,
    verify_args: bool = False,
):
    """
    Do a global normalization on the predicted values.

    Pseudocode: ``(sel_vals - median(sel_vals))/(mean(sel_vals-median(sel_vals)))``; here ``sel_vals`` denotes the values selected by the given mask.

    Parameters
    ----------
    values
        The array values to normalize.
    mask
        The mask to select the relevant values.
    sample_dims
        The dimensions alongside which the mask calculation should be done.

    Returns
    -------
    v
        The normalized values. It has the same shape and data type as the original values.
    """
    if verify_args:
        _verify_norm_args(
            values=values, mask=mask, first_dim_separates=first_dim_separates
        )

    values = values.clone()

    values[~mask] = torch.nan
    values_median = nanmedian(values, along_all_dims_except_0=first_dim_separates)

    normalized_pred = (values - values_median) / nanmean(
        (values - values_median), along_all_dims_except_0=first_dim_separates
    )
    normalized_pred[~mask] = 0

    return normalized_pred


def _verify_norm_args(
    values: torch.Tensor, mask: torch.Tensor, first_dim_separates: bool
) -> None:
    if not is_floating_array(values):
        raise ValueError(
            f"The array of values to nomralize does not contain floating point data. Actual dtype: {values.dtype}"
        )
    if not is_bool_array(mask):
        raise ValueError(
            f"The mask that selects valid values to nomralize does not contain boolean data. Actual dtype: {mask.dtype}"
        )
    if values.shape != mask.shape:
        raise ValueError(
            f"The shape of the values ({tuple(values.shape)}) is not the same as the shape of the mask ({tuple(mask.shape)})."
        )

    if first_dim_separates:
        if len(values.shape) < 2:
            raise ValueError(
                f"The value array should be at least two dimensional if the first dimension separates the samples. The current shape of the value array: {tuple(values.shape)}"
            )
    else:
        if len(values.shape) == 0:
            raise ValueError(
                f"The value array should be at least one dimensional. Current shape: {tuple(values.shape)}"
            )
