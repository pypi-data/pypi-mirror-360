from typing import Any, Protocol

import numpy as np

from ._format_checks_internal import is_bool_array, is_floating_array


class DepthLoss(Protocol):
    def __call__(
        self,
        *,
        pred: np.ndarray,
        gt: np.ndarray,
        mask: np.ndarray,
        first_dim_separates: bool = False,
        verify_args: bool = False,
    ) -> np.ndarray: ...


def dx_loss(
    *,
    pred: np.ndarray,
    gt: np.ndarray,
    mask: np.ndarray,
    x: float,
    first_dim_separates: bool = False,
    verify_args: bool = False,
) -> np.ndarray:
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

    deltas = np.zeros_like(pred)
    deltas[mask] = np.maximum(pred[mask] / gt[mask], gt[mask] / pred[mask])

    loss_vals: np.ndarray = deltas < (1.25**x)
    loss_vals = loss_vals.astype(pred.dtype)

    return _calculate_masked_mean_unchecked(
        values=loss_vals, mask=mask, first_dim_separates=first_dim_separates
    )


def mse_loss(
    *,
    pred: np.ndarray,
    gt: np.ndarray,
    mask: np.ndarray,
    first_dim_separates: bool = False,
    verify_args: bool = False,
) -> np.ndarray:
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
    pred: np.ndarray,
    gt: np.ndarray,
    mask: np.ndarray,
    first_dim_separates: bool = False,
    verify_args: bool = True,
) -> np.ndarray:
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
    x = (np.log(pred) - np.log(gt)) ** 2

    return _calculate_masked_mean_unchecked(
        values=x, mask=mask, first_dim_separates=first_dim_separates
    )


class EvalBuilder:
    """
    A class that stores the model evaluation results based on the following loss functions:

    - d1
    - d2
    - d3
    - MSE
    - MSE-log

    Parameters
    ----------
    n_items
        The total number of samples that will be added.
    dtype
        The data type of the arrays storing the loss values.

    Raises
    ------
    ValueError
        If number of items is non-positive.
    """

    def __init__(self, n_items: int, dtype: Any = np.float32) -> None:
        if n_items <= 0:
            raise ValueError("The number of items is non-positive.")

        self._data = {
            "d1": np.full((n_items,), np.nan, dtype=dtype),
            "d2": np.full((n_items,), np.nan, dtype=dtype),
            "d3": np.full((n_items,), np.nan, dtype=dtype),
            "mse": np.full((n_items,), np.nan, dtype=dtype),
            "mse_log": np.full((n_items,), np.nan, dtype=dtype),
        }
        """
        A dictionary containing the loss values. The not-yet-filled-in loss values are marked with nan. Keys and array formats:

        - ``d1``: The d1 loss values. Format: ``Scalars``
        - ``d2``: The d2 loss values. Format: ``Scalars``
        - ``d3``: The d3 loss values. Format: ``Scalars``
        - ``mse``: The mse loss values. Format: ``Scalars``
        - ``mse_log``: The mse_log loss values. Format: ``Scalars``
        """

        self._running_idx: int = 0
        """
        The index at which the addition of the elements will start in the next iteration.
        """

        self._n_items_total = n_items
        """
        The total capacity (including the number of elements already added).

        For example, if ``_running_idx=3`` and ``_n_items_total=5``, then 2 elements can be added.
        """

    @property
    def n_items_added(self) -> int:
        """
        The total number of items already added.
        """
        return self._running_idx

    @property
    def n_items_total(self) -> int:
        """
        The total number of items that can already be added.

        For example, if ``n_items_added=3`` and ``n_items_total=5``, then 2 elements can be added.
        """
        return self._n_items_total

    def push(
        self,
        pred: np.ndarray,
        gt: np.ndarray,
        mask: np.ndarray,
        first_dim_separates: bool = False,
        verify_args: bool = False,
    ) -> None:
        """
        Adds the calculated loss values based on the model outputs and ground truth data.

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

        Raises
        ------
        ValueError
            If ``verify_args`` is true and

            - Any of the arrays do not have the correct format.
            - If predicted depths, the depth masks and the ground truth depths do not have the correct shape.
            - If ``first_dim_separates=Ttrue`` and the array of predicted depths has less than 2 dimensions.
            - If too many elements are added (so the number of elements would be greater than the maximal number of elements).
        """
        if verify_args:
            self._verify_push_args(
                pred=pred, gt=gt, mask=mask, first_dim_separates=first_dim_separates
            )

        d1 = dx_loss(
            pred=pred, x=1, gt=gt, mask=mask, first_dim_separates=first_dim_separates
        )
        d2 = dx_loss(
            pred=pred, x=2, gt=gt, mask=mask, first_dim_separates=first_dim_separates
        )
        d3 = dx_loss(
            pred=pred, x=3, gt=gt, mask=mask, first_dim_separates=first_dim_separates
        )
        mse = mse_loss(
            pred=pred, gt=gt, mask=mask, first_dim_separates=first_dim_separates
        )
        mse_log = mse_log_loss(
            pred=pred, gt=gt, mask=mask, first_dim_separates=first_dim_separates
        )

        if not first_dim_separates:
            self._data["d1"][self._running_idx] = d1
            self._data["d2"][self._running_idx] = d2
            self._data["d3"][self._running_idx] = d3
            self._data["mse"][self._running_idx] = mse
            self._data["mse_log"][self._running_idx] = mse_log
            self._running_idx += 1
        else:
            n_new_samples = len(pred)

            self._data["d1"][self._running_idx : self._running_idx + n_new_samples] = d1
            self._data["d2"][self._running_idx : self._running_idx + n_new_samples] = d2
            self._data["d3"][self._running_idx : self._running_idx + n_new_samples] = d3
            self._data["mse"][
                self._running_idx : self._running_idx + n_new_samples
            ] = mse
            self._data["mse_log"][
                self._running_idx : self._running_idx + n_new_samples
            ] = mse_log

            self._running_idx += n_new_samples

    def _verify_push_args(
        self,
        pred: np.ndarray,
        gt: np.ndarray,
        mask: np.ndarray,
        first_dim_separates: bool = False,
    ):
        """
        Implements the argument verification for ``push``.
        """
        _verify_loss_args(
            pred=pred, gt=gt, mask=mask, first_dim_separates=first_dim_separates
        )

        if not first_dim_separates:
            n_items_to_add = 1
        else:
            n_items_to_add = len(pred)

        if self._running_idx + n_items_to_add > self.n_items_total:
            raise ValueError(
                f"Not enough space to store the elements. Current number of elements already added: {self._running_idx}; elements to add: {n_items_to_add}; total capacity: {self._n_items_total}"
            )

    def get_data_copy(self) -> dict[str, np.ndarray]:
        """
        Create a deep copy from the data.

        Returns
        -------
        v
            A dictionary containing the loss values. The not-yet-filled-in loss values are marked with nan. Keys and array formats:

            - ``d1``: The d1 loss values. Format: ``Scalars``
            - ``d2``: The d2 loss values. Format: ``Scalars``
            - ``d3``: The d3 loss values. Format: ``Scalars``
            - ``mse``: The mse loss values. Format: ``Scalars``
            - ``mse_log``: The mse_log loss values. Format: ``Scalars``
        """
        result: dict[str, np.ndarray] = dict()

        for key in self._data.keys():
            result[key] = self._data[key].copy()

        return result


def _verify_loss_args(
    pred: np.ndarray, gt: np.ndarray, mask: np.ndarray, first_dim_separates: bool
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
            f"The mask tensor contains non-boolean data. Dtype: {mask.dtype}"
        )
    if first_dim_separates and (len(pred.shape) < 2):
        raise ValueError(
            f"The prediction array should be at least two dimensional if the first dimension separates the samples. The current shape of the prediction array: {tuple(pred.shape)}"
        )


def _calculate_masked_mean_unchecked(
    values: np.ndarray,
    mask: np.ndarray,
    first_dim_separates: bool = False,
) -> np.ndarray:
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
        dim = tuple(range(1, len(values.shape)))
    else:
        dim = None

    values = values * mask
    return values.mean(axis=dim) * (
        np.ones_like(values).sum(axis=dim) / mask.astype(values.dtype).sum(axis=dim)
    )
