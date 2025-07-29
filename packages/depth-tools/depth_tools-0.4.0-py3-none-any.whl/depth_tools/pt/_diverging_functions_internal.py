from typing import Any

import torch


def nanmedian(a: torch.Tensor, along_all_dims_except_0: bool) -> torch.Tensor:
    """
    A nanmedian function that works similarly for both Numpy and Pytorch.

    Parameters
    ----------
    a
        The array on which the nanmedian calculation should be done.
    along_all_dims_except_0
        If true, then the median calculation is done along all dimensions, except 0. Otherwise, the median calculation is done alongside all dimensions.

    Returns
    -------
    v
        The calculated median.
    """
    if along_all_dims_except_0:
        a_reshaped = a.reshape(len(a), -1)
        nanmedian_values = torch.nanmedian(a_reshaped, dim=1).values
        new_shape: list[int] = [len(nanmedian_values)] + [1] * (len(a.shape) - 1)
        return torch.reshape(nanmedian_values, new_shape)
    else:
        return torch.nanmedian(a)


def nanmean(a: torch.Tensor, along_all_dims_except_0: bool) -> torch.Tensor:
    """
    A nanmean function that works similarly for both Numpy and Pytorch

    Parameters
    ----------
    a
        The array on which the nanmedian calculation should be done.
    along_all_dims_except_0
        If true, then the mean calculation is done along all dimensions, except 0. Otherwise, the mean calculation is done alongside all dimensions.

    Returns
    -------
    v
        The calculated median.
    """
    if along_all_dims_except_0:
        a_reshaped = a.reshape(len(a), -1)
        nanmean_values = torch.nanmean(a_reshaped, dim=1)
        new_shape: list[int] = [len(nanmean_values)] + [1] * (len(a.shape) - 1)
        return torch.reshape(nanmean_values, new_shape)
    else:
        return torch.nanmean(a)


def new_full(
    like: torch.Tensor,
    value: Any,
    shape: tuple[int, ...] | None = None,
) -> torch.Tensor:
    """
    Implements a ``full_like`` operation that plays nicely with tensor subclassing in Pytorch.

    Parameters
    ----------
    like
        The original array. Format: any array.
    value
        The value.
    shape
        The shape of the created array.
    """
    if shape is None:
        real_shape = value.shape
    else:
        real_shape = shape

    return like.new_full(real_shape, value)
