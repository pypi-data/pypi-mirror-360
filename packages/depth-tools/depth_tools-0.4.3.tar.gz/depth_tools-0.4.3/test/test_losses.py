import math
from typing import cast

import numpy as np
import torch

import depth_tools
import depth_tools.pt

from .testutil import TestBase


class TestLosses(TestBase):
    def setUp(self):
        self.gt = np.array(
            [
                [
                    [
                        [1.0, 1.0],
                        [2.0, 2.0],
                        [3.0, 1.0],
                    ]
                ],
                [
                    [
                        [1.0, 1.0],
                        [1.0, 1.0],
                        [2.0, 1.0],
                    ]
                ],
                [
                    [
                        [1.0, 3.0],
                        [1.0, 2.0],
                        [3.0, 1.0],
                    ]
                ],
                [
                    [
                        [2.0, 1.0],
                        [1.0, 1.0],
                        [2.0, 3.0],
                    ]
                ],
            ],
            dtype=np.float32,
        )

        self.pred = np.array(
            [
                [
                    [
                        [1.0, 1.0],
                        [2.0, 2.0],
                        [2.0, 1.0],
                    ]
                ],
                [
                    [
                        [3.0, 1.0],
                        [3.0, 1.0],
                        [2.0, 1.0],
                    ]
                ],
                [
                    [
                        [2.0, 3.0],
                        [3.0, 2.0],
                        [2.0, 1.0],
                    ]
                ],
                [
                    [
                        [1.0, 1.0],
                        [2.0, 1.0],
                        [3.0, 3.0],
                    ]
                ],
            ],
            dtype=np.float32,
        )

        self.mask = np.array(
            [
                [
                    [
                        [True, False],
                        [False, True],
                        [True, True],
                    ]
                ],
                [
                    [
                        [True, True],
                        [False, True],
                        [True, False],
                    ]
                ],
                [
                    [
                        [True, False],
                        [True, True],
                        [False, False],
                    ]
                ],
                [
                    [
                        [False, False],
                        [False, False],
                        [True, True],
                    ]
                ],
            ]
        )

        self.expected_mse_losses = np.array(
            [1 / 4, 4 / 4, 5 / 3, 1 / 2], dtype=np.float32
        )
        self.expected_mse_log_losses = np.array(
            [0.16440196 / 4, 1.206949 / 4, (0.480453 + 1.206949) / 3, 0.16440196 / 2],
            dtype=np.float32,
        )

        self.expected_d001_losses = np.array(
            [3 / 4, 3 / 4, 1 / 3, 1 / 2], dtype=np.float32
        )  # d_(0.01)
        self.expected_d100_losses = np.array([1, 1, 1, 1], dtype=np.float32)  # d_100

    def test_dx_loss__np__happy_path(self) -> None:
        actual_d001_losses = depth_tools.dx_loss(
            pred=self.pred, gt=self.gt, mask=self.mask, x=0.01, first_dim_separates=True
        )
        actual_d100_losses = depth_tools.dx_loss(
            pred=self.pred, gt=self.gt, mask=self.mask, x=100, first_dim_separates=True
        )
        self.assertAllclose(actual_d001_losses, self.expected_d001_losses)
        self.assertAllclose(actual_d100_losses, self.expected_d100_losses)

    def test_dx_loss__np__not_enough_dimensions(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.dx_loss(
                pred=self.pred.flatten(),
                gt=self.gt.flatten(),
                mask=self.mask.flatten(),
                x=0.01,
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)

        self.assertIn("The prediction array should be at least two dimensional", msg)

    def test_dx_loss__pt__not_enough_dimensions(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.dx_loss(
                pred=torch.from_numpy(self.pred.flatten()),
                gt=torch.from_numpy(self.gt.flatten()),
                mask=torch.from_numpy(self.mask.flatten()),
                x=0.01,
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)

        self.assertIn("The prediction array should be at least two dimensional", msg)

    def test_dx_loss__np__happy_path_single_value(self) -> None:
        actual_d001_losses = depth_tools.dx_loss(
            pred=self.pred[0], gt=self.gt[0], mask=self.mask[0], x=0.01
        )
        actual_d100_losses = depth_tools.dx_loss(
            pred=self.pred[0], gt=self.gt[0], mask=self.mask[0], x=100
        )
        self.assertAllclose(actual_d001_losses, self.expected_d001_losses[0])
        self.assertAllclose(actual_d100_losses, self.expected_d100_losses[0])

    def test_dx_loss__pt__happy_path(self) -> None:
        with torch.no_grad():
            actual_d001_losses = depth_tools.pt.dx_loss(
                pred=torch.from_numpy(self.pred),
                gt=torch.from_numpy(self.gt),
                mask=torch.from_numpy(self.mask),
                x=0.01,
                first_dim_separates=True,
                verify_args=True,
            ).numpy()
            actual_d100_losses = depth_tools.pt.dx_loss(
                pred=torch.from_numpy(self.pred),
                gt=torch.from_numpy(self.gt),
                mask=torch.from_numpy(self.mask),
                first_dim_separates=True,
                verify_args=True,
                x=100,
            ).numpy()

        self.assertAllclose(actual_d001_losses, self.expected_d001_losses)
        self.assertAllclose(actual_d100_losses, self.expected_d100_losses)

    def test_dx_loss__np__invalid_arrays(self):
        def fn(pred, gt, mask):
            depth_tools.dx_loss(pred=pred, gt=gt, mask=mask, verify_args=True, x=0.7)

        self.probe_invalid_inputs([self.pred, self.gt, self.mask], fn)

    def test_dx_loss__pt__invalid_arrays(self):
        def fn(pred, gt, mask):
            depth_tools.pt.dx_loss(
                pred=torch.from_numpy(pred),
                gt=torch.from_numpy(gt),
                mask=torch.from_numpy(mask),
                verify_args=True,
                x=0.7,
            )

        self.probe_invalid_inputs([self.pred, self.gt, self.mask], fn)

    def test_mse_loss__np__happy_path(self):
        actual_mse_losses = depth_tools.mse_loss(
            pred=self.pred, gt=self.gt, mask=self.mask, first_dim_separates=True
        )
        self.assertAllclose(actual_mse_losses, self.expected_mse_losses)

    def test_mse_loss__np__happy_path__single_value(self):
        actual_mse_losses = depth_tools.mse_loss(
            pred=self.pred[0], gt=self.gt[0], mask=self.mask[0]
        )
        self.assertAllclose(actual_mse_losses, self.expected_mse_losses[0])

    def test_mse_loss__pt__happy_path(self):
        with torch.no_grad():
            actual_mse_losses = depth_tools.pt.mse_loss(
                pred=torch.from_numpy(self.pred),
                gt=torch.from_numpy(self.gt),
                mask=torch.from_numpy(self.mask),
                first_dim_separates=True,
                verify_args=True,
            ).numpy()
        self.assertAllclose(actual_mse_losses, self.expected_mse_losses)

    def test_mse_loss__np__not_enough_dimensions(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.mse_loss(
                pred=self.pred.flatten(),
                gt=self.gt.flatten(),
                mask=self.mask.flatten(),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)

        self.assertIn("The prediction array should be at least two dimensional", msg)

    def test_mse_loss__pt__not_enough_dimensions(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.mse_loss(
                pred=torch.from_numpy(self.pred.flatten()),
                gt=torch.from_numpy(self.gt.flatten()),
                mask=torch.from_numpy(self.mask.flatten()),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)

        self.assertIn("The prediction array should be at least two dimensional", msg)

    def test_mse_loss__np__invalid_arrays(self):
        def fn(pred, gt, mask):
            depth_tools.mse_loss(pred=pred, gt=gt, mask=mask, verify_args=True)

        self.probe_invalid_inputs([self.pred, self.gt, self.mask], fn)

    def test_mse_loss__pt__invalid_arrays(self):
        def fn(pred, gt, mask):
            with torch.no_grad():
                depth_tools.pt.mse_loss(
                    pred=torch.from_numpy(pred),
                    gt=torch.from_numpy(gt),
                    mask=torch.from_numpy(mask),
                    verify_args=True,
                    first_dim_separates=True,
                )

        self.probe_invalid_inputs([self.pred, self.gt, self.mask], fn)

    def test_mse_log_loss__np__happy_path(self):
        actual_mse_log_losses = depth_tools.mse_log_loss(
            pred=self.pred, gt=self.gt, mask=self.mask, first_dim_separates=True
        )
        self.assertAllclose(actual_mse_log_losses, self.expected_mse_log_losses)

    def test_mse_log_loss__pt__happy_path(self):
        with torch.no_grad():
            actual_mse_log_losses = depth_tools.pt.mse_log_loss(
                pred=torch.from_numpy(self.pred),
                gt=torch.from_numpy(self.gt),
                mask=torch.from_numpy(self.mask),
                first_dim_separates=True,
                verify_args=True,
            ).numpy()
        self.assertAllclose(actual_mse_log_losses, self.expected_mse_log_losses)

    def test_mse_log_loss__np__not_enough_dimensions(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.mse_log_loss(
                pred=self.pred.flatten(),
                gt=self.gt.flatten(),
                mask=self.mask.flatten(),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)

        self.assertIn("The prediction array should be at least two dimensional", msg)

    def test_mse_log_loss__pt__not_enough_dimensions(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.mse_log_loss(
                pred=torch.from_numpy(self.pred.flatten()),
                gt=torch.from_numpy(self.gt.flatten()),
                mask=torch.from_numpy(self.mask.flatten()),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)

        self.assertIn("The prediction array should be at least two dimensional", msg)

    def test_mse_log_loss__np__invalid_arrays(self):
        def fn(pred, gt, mask):
            depth_tools.mse_log_loss(pred=pred, gt=gt, mask=mask, verify_args=True)

        self.probe_invalid_inputs([self.pred, self.gt, self.mask], fn)

    def test_mse_log_loss__pt__invalid_arrays(self):
        def fn(pred, gt, mask):
            with torch.no_grad():
                depth_tools.pt.mse_log_loss(
                    pred=torch.from_numpy(pred),
                    gt=torch.from_numpy(gt),
                    mask=torch.from_numpy(mask),
                    verify_args=True,
                )

        self.probe_invalid_inputs([self.pred, self.gt, self.mask], fn)

    def test_calculate_masked_mean__np__nosep(self):
        arr = np.full((30, 40), 0.1, dtype=np.float32)
        mask = np.full((30, 40), True, dtype=np.bool_)

        arr[:, 1] = 10000
        mask[:, 1] = False

        actual_mean = cast(
            float,
            depth_tools._losses_univ._calculate_masked_mean_unchecked(
                values=arr, mask=mask, first_dim_separates=False
            ).item(),
        )
        expected_mean = 0.1

        self.assertAlmostEqual(actual_mean, expected_mean)

    def test_calculate_masked_mean__np__sep(self):
        arr = np.full((30, 40), 0.1, dtype=np.float32)
        mask = np.full((30, 40), True, dtype=np.bool_)

        arr[:, 1] = 10000
        mask[:, 1] = False

        actual_mean = depth_tools._losses_univ._calculate_masked_mean_unchecked(
            values=arr, mask=mask, first_dim_separates=True
        )
        expected_mean = np.full((30), 0.1, dtype=np.float32)

        self.assertAllclose(actual_mean, expected_mean)

    def test_calculate_masked_mean__pt__nosep(self):
        arr = np.full((30, 40), 0.1, dtype=np.float32)
        mask = np.full((30, 40), True, dtype=np.bool_)

        arr[:, 1] = 10000
        mask[:, 1] = False

        actual_mean = cast(
            float,
            depth_tools.pt._losses_univ._calculate_masked_mean_unchecked(
                values=torch.from_numpy(arr),
                mask=torch.from_numpy(mask),
                first_dim_separates=False,
            ).item(),
        )
        expected_mean = 0.1

        self.assertAlmostEqual(actual_mean, expected_mean)

    def test_calculate_masked_mean__pt__sep(self):
        arr = np.full((30, 40), 0.1, dtype=np.float32)
        mask = np.full((30, 40), True, dtype=np.bool_)

        arr[:, 1] = 10000
        mask[:, 1] = False

        actual_mean = depth_tools.pt._losses_univ._calculate_masked_mean_unchecked(
            values=torch.from_numpy(arr),
            mask=torch.from_numpy(mask),
            first_dim_separates=True,
        ).numpy()
        expected_mean = np.full((30), 0.1, dtype=np.float32)

        self.assertAllclose(actual_mean, expected_mean)


class TestEvalBuilder(TestBase):
    def setUp(self):
        self.preds = np.array(
            [
                [1, 2, 3],
                [2, 4, 5],
                [3, 6, 7],
            ],
            dtype=np.float32,
        )
        self.gts = np.array(
            [
                [1, 2, 3],
                [2, 10, 5],
                [3, 25, 4],
            ],
            dtype=np.float32,
        )
        self.masks = np.array(
            [
                [True, True, True],
                [True, True, True],
                [True, True, True],
            ],
            dtype=np.bool_,
        )

        self.d1 = depth_tools.dx_loss(
            gt=self.gts,
            pred=self.preds,
            mask=self.masks,
            x=1,
            first_dim_separates=True,
            verify_args=True,
        )
        self.d2 = depth_tools.dx_loss(
            gt=self.gts,
            pred=self.preds,
            mask=self.masks,
            x=2,
            first_dim_separates=True,
            verify_args=True,
        )
        self.d3 = depth_tools.dx_loss(
            gt=self.gts,
            pred=self.preds,
            mask=self.masks,
            x=3,
            first_dim_separates=True,
            verify_args=True,
        )
        self.mse = depth_tools.mse_loss(
            gt=self.gts,
            pred=self.preds,
            mask=self.masks,
            first_dim_separates=True,
            verify_args=True,
        )
        self.mse_log = depth_tools.mse_log_loss(
            gt=self.gts,
            pred=self.preds,
            mask=self.masks,
            first_dim_separates=True,
            verify_args=True,
        )

        self.eval_builder_np = depth_tools.EvalBuilder(n_items=3)
        self.eval_builder_pt = depth_tools.pt.EvalBuilder(n_items=3)

    def test_init__np__n_items_0(self):
        with self.assertRaises(ValueError):
            depth_tools.EvalBuilder(n_items=0, dtype=np.float32)

    def test_init__np__n_items_negative(self):
        with self.assertRaises(ValueError):
            depth_tools.EvalBuilder(n_items=-1, dtype=np.float32)

    def test_init__pt__n_items_0(self):
        with self.assertRaises(ValueError):
            depth_tools.pt.EvalBuilder(n_items=0, dtype=np.float32)

    def test_init__pt__n_items_negative(self):
        with self.assertRaises(ValueError):
            depth_tools.pt.EvalBuilder(n_items=-1, dtype=np.float32)

    def test_push__np__happy_path__allonce(self) -> None:
        self.eval_builder_np.push(
            pred=self.preds,
            gt=self.gts,
            mask=self.masks,
            first_dim_separates=True,
            verify_args=True,
        )

        self.assertEqual(self.eval_builder_np.n_items_added, 3)
        self.verify_calculated_losses(self.eval_builder_np)

    def test_push__pt__happy_path__allonce(self) -> None:
        self.eval_builder_pt.push(
            pred=torch.from_numpy(self.preds),
            gt=torch.from_numpy(self.gts),
            mask=torch.from_numpy(self.masks),
            first_dim_separates=True,
            verify_args=True,
        )

        self.assertEqual(self.eval_builder_pt.n_items_added, 3)
        self.verify_calculated_losses(self.eval_builder_pt)

    def test_push__np__happy_path__add11(self) -> None:
        self.eval_builder_np.push(
            pred=self.preds[0], gt=self.gts[0], mask=self.masks[0], verify_args=True
        )
        self.eval_builder_np.push(
            pred=self.preds[1], gt=self.gts[1], mask=self.masks[1], verify_args=True
        )

        self.assertEqual(self.eval_builder_np.n_items_added, 2)
        self.verify_calculated_losses(self.eval_builder_np)

    def test_push__np__happy_path__add12(self) -> None:
        self.eval_builder_np.push(
            pred=self.preds[0],
            gt=self.gts[0],
            mask=self.masks[0],
            verify_args=True,
        )
        self.eval_builder_np.push(
            pred=self.preds[1:3],
            gt=self.gts[1:3],
            mask=self.masks[1:3],
            verify_args=True,
            first_dim_separates=True,
        )

        self.assertEqual(self.eval_builder_np.n_items_added, 3)
        self.verify_calculated_losses(self.eval_builder_np)

    def test_push__pt__happy_path__add11(self) -> None:
        self.eval_builder_pt.push(
            pred=torch.from_numpy(self.preds[0]),
            gt=torch.from_numpy(self.gts[0]),
            mask=torch.from_numpy(self.masks[0]),
            verify_args=True,
        )
        self.eval_builder_pt.push(
            pred=torch.from_numpy(self.preds[1]),
            gt=torch.from_numpy(self.gts[1]),
            mask=torch.from_numpy(self.masks[1]),
            verify_args=True,
        )

        self.assertEqual(self.eval_builder_pt.n_items_added, 2)
        self.verify_calculated_losses(self.eval_builder_pt)

    def test_push__pt__happy_path__add12(self) -> None:
        self.eval_builder_pt.push(
            pred=torch.from_numpy(self.preds[0]),
            gt=torch.from_numpy(self.gts[0]),
            mask=torch.from_numpy(self.masks[0]),
        )
        self.eval_builder_pt.push(
            pred=torch.from_numpy(self.preds[1:3]),
            gt=torch.from_numpy(self.gts[1:3]),
            mask=torch.from_numpy(self.masks[1:3]),
            verify_args=True,
            first_dim_separates=True,
        )

        self.assertEqual(self.eval_builder_pt.n_items_added, 3)
        self.verify_calculated_losses(self.eval_builder_pt)

    def test_push__np__invalid_shape(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_np.push(
                pred=self.preds.flatten(),
                gt=self.gts.flatten(),
                mask=self.masks.flatten(),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The prediction array should be at least two dimensional", msg)

    def test_push__np__invalid_pred_dtype(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_np.push(
                pred=self.preds.astype(np.int32),
                gt=self.gts,
                mask=self.masks,
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The prediction tensor does not contain floating", msg)

    def test_push__np__invalid_gt_dtype(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_np.push(
                pred=self.preds,
                gt=self.gts.astype(np.int32),
                mask=self.masks,
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The ground truth tensor does not contain floating", msg)

    def test_push__np__invalid_mask_dtype(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_np.push(
                pred=self.preds,
                gt=self.gts,
                mask=self.masks.astype(np.int32),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("mask tensor contains non-boolean", msg)

    def test_push__np__gt_inconsistent_shape(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_np.push(
                pred=self.preds,
                gt=self.gts.flatten(),
                mask=self.masks,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The shape of the ground truths", msg)

    def test_push__np__mask_inconsistent_shape(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_np.push(
                pred=self.preds,
                gt=self.gts,
                mask=self.masks.flatten(),
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The shape of the mask", msg)

    def test_push__np__too_many_elements_nosep(self) -> None:
        self.eval_builder_np.push(
            pred=self.preds[:2],
            gt=self.gts[:2],
            mask=self.masks[:2],
            verify_args=True,
            first_dim_separates=True,
        )
        self.eval_builder_np.push(
            pred=self.preds[0],
            gt=self.gts[0],
            mask=self.masks[0],
            verify_args=True,
        )
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_np.push(
                pred=self.preds[0],
                gt=self.gts[0],
                mask=self.masks[0],
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("Not enough space to store the elements", msg)

    def test_push__np__too_many_elements_sep(self) -> None:
        self.eval_builder_np.push(
            pred=self.preds[0],
            gt=self.gts[0],
            mask=self.masks[0],
            verify_args=True,
        )
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_np.push(
                pred=self.preds,
                gt=self.gts,
                mask=self.masks,
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("Not enough space to store the elements", msg)

    def test_push__pt__invalid_shape(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_pt.push(
                pred=torch.from_numpy(self.preds.flatten()),
                gt=torch.from_numpy(self.gts.flatten()),
                mask=torch.from_numpy(self.masks.flatten()),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The prediction array should be at least two dimensional", msg)

    def test_push__pt__invalid_pred_dtype(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_pt.push(
                pred=torch.from_numpy(self.preds.astype(np.int32)),
                gt=torch.from_numpy(self.gts),
                mask=torch.from_numpy(self.masks),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The prediction tensor does not contain floating", msg)

    def test_push__pt__invalid_gt_dtype(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_pt.push(
                pred=torch.from_numpy(self.preds),
                gt=torch.from_numpy(self.gts.astype(np.int32)),
                mask=torch.from_numpy(self.masks),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The ground truth tensor does not contain floating", msg)

    def test_push__pt__invalid_mask_dtype(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_pt.push(
                pred=torch.from_numpy(self.preds),
                gt=torch.from_numpy(self.gts),
                mask=torch.from_numpy(self.masks.astype(np.int32)),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("mask tensor contains non-boolean", msg)

    def test_push__pt__gt_inconsistent_shape(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_pt.push(
                pred=torch.from_numpy(self.preds),
                gt=torch.from_numpy(self.gts.flatten()),
                mask=torch.from_numpy(self.masks),
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The shape of the ground truths", msg)

    def test_push__pt__mask_inconsistent_shape(self) -> None:
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_pt.push(
                pred=torch.from_numpy(self.preds),
                gt=torch.from_numpy(self.gts),
                mask=torch.from_numpy(self.masks.flatten()),
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The shape of the mask", msg)

    def test_push__pt__too_many_elements_nosep(self) -> None:
        self.eval_builder_pt.push(
            pred=torch.from_numpy(self.preds[:2]),
            gt=torch.from_numpy(self.gts[:2]),
            mask=torch.from_numpy(self.masks[:2]),
            verify_args=True,
            first_dim_separates=True,
        )
        self.eval_builder_pt.push(
            pred=torch.from_numpy(self.preds[0]),
            gt=torch.from_numpy(self.gts[0]),
            mask=torch.from_numpy(self.masks[0]),
            verify_args=True,
        )
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_pt.push(
                pred=torch.from_numpy(self.preds[0]),
                gt=torch.from_numpy(self.gts[0]),
                mask=torch.from_numpy(self.masks[0]),
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("Not enough space to store the elements", msg)

    def test_push__pt__too_many_elements_sep(self) -> None:
        self.eval_builder_pt.push(
            pred=torch.from_numpy(self.preds[0]),
            gt=torch.from_numpy(self.gts[0]),
            mask=torch.from_numpy(self.masks[0]),
            verify_args=True,
        )
        with self.assertRaises(ValueError) as cm:
            self.eval_builder_pt.push(
                pred=torch.from_numpy(self.preds),
                gt=torch.from_numpy(self.gts),
                mask=torch.from_numpy(self.masks),
                first_dim_separates=True,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("Not enough space to store the elements", msg)

    def test_gradients_present__mse(self):
        preds_pt = torch.from_numpy(self.preds).requires_grad_(True)
        gts_pt = torch.from_numpy(self.gts).requires_grad_(True)

        self.eval_builder_pt.push(
            pred=preds_pt[0],
            gt=gts_pt[0],
            mask=torch.from_numpy(self.masks[0]),
        )
        self.eval_builder_pt.push(
            pred=preds_pt[1:3],
            gt=gts_pt[1:3],
            mask=torch.from_numpy(self.masks[1:3]),
        )

        self.assertIsNone(preds_pt.grad)
        self.assertIsNone(gts_pt.grad)

        data = self.eval_builder_pt.get_data_copy()

        data["mse"].mean().backward()

        self.assertIsNotNone(preds_pt.grad)
        self.assertIsNotNone(gts_pt.grad)
        self.assertAny(np.array(preds_pt.grad) > 0)
        self.assertAny(np.array(gts_pt.grad) > 0)

    def test_gradients_present__mse_log(self):
        preds_pt = torch.from_numpy(self.preds).requires_grad_(True)
        gts_pt = torch.from_numpy(self.gts).requires_grad_(True)

        self.eval_builder_pt.push(
            pred=preds_pt[0],
            gt=gts_pt[0],
            mask=torch.from_numpy(self.masks[0]),
        )
        self.eval_builder_pt.push(
            pred=preds_pt[1:3],
            gt=gts_pt[1:3],
            mask=torch.from_numpy(self.masks[1:3]),
        )

        self.assertIsNone(preds_pt.grad)
        self.assertIsNone(gts_pt.grad)

        data = self.eval_builder_pt.get_data_copy()

        data["mse_log"].mean().backward()

        self.assertIsNotNone(preds_pt.grad)
        self.assertIsNotNone(gts_pt.grad)
        self.assertAny(np.array(preds_pt.grad) > 0)
        self.assertAny(np.array(gts_pt.grad) > 0)

    def verify_calculated_losses(
        self, eval_builder: depth_tools.EvalBuilder | depth_tools.pt.EvalBuilder
    ) -> None:
        self.assertLessEqual(eval_builder.n_items_added, eval_builder.n_items_total)
        self.assertEqual(eval_builder.n_items_total, 3)

        if isinstance(eval_builder, depth_tools.EvalBuilder):
            data = eval_builder.get_data_copy()
            for i in range(eval_builder.n_items_added):
                self.assertAlmostEqual(self.d1[i].item(), data["d1"][i].item())
                self.assertAlmostEqual(self.d2[i].item(), data["d2"][i].item())
                self.assertAlmostEqual(self.d3[i].item(), data["d3"][i].item())
                self.assertAlmostEqual(self.mse[i].item(), data["mse"][i].item())
                self.assertAlmostEqual(
                    self.mse_log[i].item(), data["mse_log"][i].item()
                )
            if eval_builder.n_items_added < eval_builder.n_items_total:
                for i in range(eval_builder.n_items_added, eval_builder.n_items_total):
                    self.assertIsNan(data["d1"][i].item())
                    self.assertIsNan(data["d2"][i].item())
                    self.assertIsNan(data["d3"][i].item())
                    self.assertIsNan(data["mse"][i].item())
                    self.assertIsNan(data["mse_log"][i].item())
        else:
            data = eval_builder.get_data_copy()
            for i in range(eval_builder.n_items_added):
                self.assertAlmostEqual(self.d1[i].item(), data["d1"][i].numpy().item())
                self.assertAlmostEqual(self.d2[i].item(), data["d2"][i].numpy().item())
                self.assertAlmostEqual(self.d3[i].item(), data["d3"][i].numpy().item())
                self.assertAlmostEqual(
                    self.mse[i].item(), data["mse"][i].numpy().item()
                )
                self.assertAlmostEqual(
                    self.mse_log[i].item(), data["mse_log"][i].numpy().item()
                )
            if eval_builder.n_items_added < eval_builder.n_items_total:
                for i in range(eval_builder.n_items_added, eval_builder.n_items_total):
                    self.assertIsNan(cast(float, data["d1"][i].numpy().item()))
                    self.assertIsNan(cast(float, data["d2"][i].numpy().item()))
                    self.assertIsNan(cast(float, data["d3"][i].numpy().item()))
                    self.assertIsNan(cast(float, data["mse"][i].item()))
                    self.assertIsNan(cast(float, data["mse_log"][i].item()))

    def assertIsNan(self, value: float) -> None:
        if not math.isnan(value):
            raise self.failureException(f"The value ({value}) is not NaN.")
