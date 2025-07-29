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
