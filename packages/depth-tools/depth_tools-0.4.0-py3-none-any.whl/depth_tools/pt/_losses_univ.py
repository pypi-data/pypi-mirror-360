# The file is automatically generated from src\depth_tools\_losses_univ.py; do not edit.
from typing import Protocol, Sequence, SupportsIndex

import torch

from ._format_checks_internal import is_bool_array, is_floating_array


class DepthLoss(Protocol):
    def __call__(
        self,
        *,
        pred: torch.Tensor,
        gt: torch.Tensor,
        mask: torch.Tensor,
        first_dim_separates: bool = False,
        verify_args: bool = False,
    ) -> torch.Tensor: ...


def dx_loss(
    *,
    pred: torch.Tensor,
    gt: torch.Tensor,
    mask: torch.Tensor,
    x: float,
    first_dim_separates: bool = False,
    verify_args: bool = False,
) -> torch.Tensor:
    """
    Calculate the non-differentiable $\\delta_x$ loss.

    This function expects the arguments to have the same shape, so broadcast is not necessary.

    This function does not do any additional reductions.

    Parameters
    ----------
    pred
        The predicted values. Format: the array should contain floating data. If ``first_dim_separates``, then it should have at least two dimensions.
    gt
        The ground truth values. Format: the array should contain floating data. If ``first_dim_separates``, then it should have at least two dimensions. It should have the same shape as the predicted values.
    mask
        The masks that select the relevant pixels. Format: the array should contain boolean data. If ``first_dim_separates``, then it should have at least two dimensions. It should have the same shape as the predicted values.
    x
        The ``x`` parameter of the loss.
    first_dim_separates
        If this is true, then the loss calculation is done for each element along dimension 0 individually. Otherwise the claculation is done for the whole array globally.
    verify_args
        If this is true, then the function verifies the arguments and raises errors if the shapes or data types are incorrect. Otherwise the possible errors are treated as implementation detail.

    Return
    ------
    v
        The final losses. Format: ``Scalars``
    """
    if verify_args:
        _verify_loss_args(
            gt=gt, pred=pred, mask=mask, first_dim_separates=first_dim_separates
        )

    deltas = torch.zeros_like(pred)
    deltas[mask] = torch.maximum(pred[mask] / gt[mask], gt[mask] / pred[mask])

    loss_vals: torch.Tensor = deltas < (1.25**x)
    loss_vals = loss_vals.to(pred.dtype)

    return _calculate_masked_mean_unchecked(
        values=loss_vals, mask=mask, first_dim_separates=first_dim_separates
    )


def mse_loss(
    *,
    pred: torch.Tensor,
    gt: torch.Tensor,
    mask: torch.Tensor,
    first_dim_separates: bool = False,
    verify_args: bool = False,
) -> torch.Tensor:
    """
    Calculate the masked MSE loss. Unlike the similar Pytorch function, this function does not do any aggregation.

    This function expects the arguments to have the same shape, so broadcast is not necessary.

    This function does not do any additional reductions.

    Parameters
    ----------
    pred
        The predicted values. Format: the array should contain floating data. If ``first_dim_separates``, then it should have at least two dimensions.
    gt
        The ground truth values. Format: the array should contain floating data. If ``first_dim_separates``, then it should have at least two dimensions. It should have the same shape as the predicted values.
    mask
        The masks that select the relevant pixels. Format: the array should contain boolean data. If ``first_dim_separates``, then it should have at least two dimensions. It should have the same shape as the predicted values.
    first_dim_separates
        If this is true, then the loss calculation is done for each element along dimension 0 individually. Otherwise the claculation is done for the whole array globally.
    verify_args
        If this is true, then the function verifies the arguments and raises errors if the shapes or data types are incorrect. Otherwise the possible errors are treated as implementation detail.

    Return
    ------
    v
        The final losses. Format: ``Scalars``
    """
    if verify_args:
        _verify_loss_args(
            gt=gt, pred=pred, mask=mask, first_dim_separates=first_dim_separates
        )

    x = (pred - gt) ** 2

    return _calculate_masked_mean_unchecked(
        values=x, mask=mask, first_dim_separates=first_dim_separates
    )


def mse_log_loss(
    pred: torch.Tensor,
    gt: torch.Tensor,
    mask: torch.Tensor,
    first_dim_separates: bool = False,
    verify_args: bool = True,
) -> torch.Tensor:
    """
    Calculate the masked MSE loss. Unlike the similar Pytorch function, this function does not do any aggregation.

    This function expects the arguments to have the same shape, so broadcast is not necessary.

    This function does not do any additional reductions.

    Parameters
    ----------
    pred
        The predicted values. Format: the array should contain floating data. If ``first_dim_separates``, then it should have at least two dimensions.
    gt
        The ground truth values. Format: the array should contain floating data. If ``first_dim_separates``, then it should have at least two dimensions. It should have the same shape as the predicted values.
    mask
        The masks that select the relevant pixels. Format: the array should contain boolean data. If ``first_dim_separates``, then it should have at least two dimensions. It should have the same shape as the predicted values.
    first_dim_separates
        If this is true, then the loss calculation is done for each element along dimension 0 individually. Otherwise the claculation is done for the whole array globally.
    verify_args
        If this is true, then the function verifies the arguments and raises errors if the shapes or data types are incorrect. Otherwise the possible errors are treated as implementation detail.

    Return
    ------
    v
        The final losses. Format: ``Scalars_Float``
    """
    if verify_args:
        _verify_loss_args(
            gt=gt, pred=pred, mask=mask, first_dim_separates=first_dim_separates
        )
    x = (torch.log(pred) - torch.log(gt)) ** 2

    return _calculate_masked_mean_unchecked(
        values=x, mask=mask, first_dim_separates=first_dim_separates
    )


def _verify_loss_args(
    pred: torch.Tensor, gt: torch.Tensor, mask: torch.Tensor, first_dim_separates: bool
) -> None:
    """
    Throws `ValueError` if the loss arguments do not have the proper format.
    """
    if pred.shape != gt.shape:
        raise ValueError(
            f"The shape of the ground truths ({gt.shape}) is not equal the shape of the predictions ({tuple(pred.shape)})."
        )
    if mask.shape != pred.shape:
        raise ValueError(
            f"The shape of the mask ({mask.shape}) is not equal the shape of the predictions ({tuple(pred.shape)})."
        )

    if not is_floating_array(pred):
        raise ValueError(
            f"The prediction tensor does not contain floating point data. Dtype: {pred.dtype}"
        )
    if not is_floating_array(gt):
        raise ValueError(
            f"The ground truth tensor does not contain floating point data. Dtype: {gt.dtype}"
        )
    if not is_bool_array(mask):
        raise ValueError(
            f"The mask tensor contains neither floating point, nor boolean data. Dtype: {mask.dtype}"
        )
    if first_dim_separates and (len(pred.shape) < 2):
        raise ValueError(
            f"The prediction array should be at least two dimensional if the first dimension separates the samples. The current shape of the prediction array: {tuple(pred.shape)}"
        )


def _calculate_masked_mean_unchecked(
    values: torch.Tensor,
    mask: torch.Tensor,
    first_dim_separates: bool = False,
) -> torch.Tensor:
    """
    A function that calculates the masked mean of the given values.

    This function does not check its arguments.

    Parameters
    ----------
    values
        The values of which the mean should be calculated. Format: the array should contain floating data. If ``first_dim_separates``, then it should have at least two dimensions. It should have the same shape as the predicted values.
    mask
        The masks that select the relevant values. Format: the array should contain boolean data. If ``first_dim_separates``, then it should have at least two dimensions. It should have the same shape as the predicted values.
    first_dim_separates
        If this is true, then the mean calculation is done for each element along dimension 0 individually. Otherwise the claculation is done for the whole array globally.
    """

    if first_dim_separates:
        dim = tuple(values.shape)[1:]
    else:
        dim = None

    values = values * mask
    return values.mean(dim=dim) * (
        torch.ones_like(values).sum(dim=dim) / mask.to(values.dtype).sum(dim=dim)
    )
