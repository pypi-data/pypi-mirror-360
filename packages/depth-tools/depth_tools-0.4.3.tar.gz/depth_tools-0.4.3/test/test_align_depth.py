import math

import npy_unittest
import numpy as np
import torch

import depth_tools
import depth_tools.pt


class TestAlignDepth(npy_unittest.NpyTestCase):
    def setUp(self):
        self.rng = np.random.default_rng(30)

        self.gt_values = self.rng.uniform(0.1, 25, (1, 120, 160))
        self.pred_values = self.gt_values * 2 + 10
        self.mask = self.rng.uniform(0, 1, self.gt_values.shape) > 0.5

        self.expected_shift = np.array(-5, dtype=np.float32)
        self.expected_scale = np.array(0.5, dtype=np.float32)

        self.multiple_gt_arrs = self.rng.uniform(0.1, 25, (3, 1, 120, 160))
        self.multiple_pred_arrs = self.multiple_gt_arrs * np.array(
            [[[[3]]], [[[7]]], [[[1]]]]
        ) + np.array([[[[8]]], [[[5]]], [[[2]]]])
        self.multiple_masks = self.rng.uniform(0, 1, self.multiple_gt_arrs.shape) > 0.5
        self.expected_shifts = np.array([-8 / 3, -5 / 7, -2 / 1], dtype=np.float32)
        self.expected_scales = np.array([1 / 3, 1 / 7, 1 / 1], dtype=np.float32)

    def test_align_shift_scale__multiple_arrays(self) -> None:
        with self.assertNoLogs():
            aligned_maps, actual_shifts, actual_scales = depth_tools.align_shift_scale(
                mask=self.multiple_masks,
                control_mask=None,
                gt_values=self.multiple_gt_arrs,
                pred_values=self.multiple_pred_arrs,
                verify_args=True,
                first_dim_separates=True,
            )
        self.assertAllclose(
            aligned_maps[self.multiple_masks],
            self.multiple_gt_arrs[self.multiple_masks],
            atol=1e-4,
        )
        self.assertAllclose(actual_shifts, self.expected_shifts)
        self.assertAllclose(actual_scales, self.expected_scales)

    def test_align_shift_scale__multiple_arrays_pt(self) -> None:
        with self.assertNoLogs():
            aligned_maps, actual_shifts, actual_scales = (
                depth_tools.pt.align_shift_scale(
                    mask=torch.from_numpy(self.multiple_masks),
                    control_mask=None,
                    gt_values=torch.from_numpy(self.multiple_gt_arrs),
                    pred_values=torch.from_numpy(self.multiple_pred_arrs),
                    verify_args=True,
                    first_dim_separates=True,
                )
            )
        self.assertAllclose(
            aligned_maps.numpy()[self.multiple_masks],
            self.multiple_gt_arrs[self.multiple_masks],
            atol=1e-4,
        )
        self.assertAllclose(actual_shifts.numpy(), self.expected_shifts)
        self.assertAllclose(actual_scales.numpy(), self.expected_scales)

    def test_align_shift_scale__happy_path__no_control_mask(self):
        with self.assertNoLogs():
            aligned_map, actual_shift, actual_scale = depth_tools.align_shift_scale(
                mask=self.mask,
                control_mask=None,
                gt_values=self.gt_values,
                pred_values=self.pred_values,
                verify_args=True,
            )

        self.assertAllclose(
            aligned_map[self.mask], self.gt_values[self.mask], atol=1e-4
        )
        self.assertAllclose(actual_shift, self.expected_shift)
        self.assertAllclose(actual_scale, self.expected_scale)

    def test_align_shift_scale__happy_path__no_control_mask_pt(self):
        with self.assertNoLogs():
            with torch.no_grad():
                aligned_map, actual_shift, actual_scale = (
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
                )
        aligned_map = aligned_map.numpy()

        self.assertAllclose(
            aligned_map[self.mask], self.gt_values[self.mask], atol=1e-4
        )
        self.assertAllclose(actual_shift.numpy(), self.expected_shift)
        self.assertAllclose(actual_scale.numpy(), self.expected_scale)

    def test_align_shift_scale__happy_path__control_mask(self):
        control_mask = (
            self.rng.uniform(0, 1, size=self.pred_values.shape) > 0.5
        ) & self.mask

        self.pred_values[(~control_mask) & self.mask] = 50000

        with self.assertNoLogs():
            aligned_map, actual_shift, actual_scale = depth_tools.align_shift_scale(
                mask=self.mask,
                control_mask=control_mask,
                gt_values=self.gt_values,
                pred_values=self.pred_values,
                verify_args=True,
            )

        self.assertAllclose(
            aligned_map[control_mask & self.mask],
            self.gt_values[control_mask & self.mask],
            atol=1e-4,
        )
        self.assertAllclose(actual_shift, self.expected_shift)
        self.assertAllclose(actual_scale, self.expected_scale)

    def test_align_shift_scale__happy_path__control_mask_pt(self):
        control_mask = (
            self.rng.uniform(0, 1, size=self.pred_values.shape) > 0.5
        ) & self.mask

        self.pred_values[(~control_mask) & self.mask] = 50000

        with self.assertNoLogs():
            with torch.no_grad():
                aligned_map, actual_shift, actual_scale = (
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=torch.from_numpy(control_mask),
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
                )
        aligned_map = aligned_map.numpy()

        self.assertAllclose(
            aligned_map[control_mask & self.mask],
            self.gt_values[control_mask & self.mask],
            atol=1e-4,
        )
        self.assertAllclose(actual_shift.numpy(), self.expected_shift)
        self.assertAllclose(actual_scale.numpy(), self.expected_scale)

    def test_align_shift_scale__invalid_shape(self):
        with self.subTest("invalid_pred_values"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.align_shift_scale(
                        mask=self.mask,
                        control_mask=None,
                        gt_values=self.gt_values,
                        pred_values=self.pred_values.flatten(),
                        verify_args=True,
                    )
        with self.subTest("invalid_gt_values"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.align_shift_scale(
                        mask=self.mask,
                        control_mask=None,
                        gt_values=self.gt_values.flatten(),
                        pred_values=self.pred_values,
                        verify_args=True,
                    )
        with self.subTest("invalid_mask"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.align_shift_scale(
                        mask=self.mask.flatten(),
                        control_mask=None,
                        gt_values=self.gt_values,
                        pred_values=self.pred_values,
                        verify_args=True,
                    )
        with self.subTest("invalid_control_mask"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.align_shift_scale(
                        mask=self.mask,
                        control_mask=self.mask.flatten(),
                        gt_values=self.gt_values,
                        pred_values=self.pred_values,
                        verify_args=True,
                    )

    def test_align_shift_scale__invalid_shape_pt(self):
        with self.subTest("invalid_pred_values"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values.flatten()),
                        verify_args=True,
                    )
        with self.subTest("invalid_gt_values"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values.flatten()),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_mask"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask.flatten()),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_control_mask"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=torch.from_numpy(self.mask.flatten()),
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )

    def test_align_shift_scale__invalid_dtype(self):
        with self.subTest("invalid_pred_values"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.align_shift_scale(
                        mask=self.mask,
                        control_mask=None,
                        gt_values=self.gt_values,
                        pred_values=self.pred_values.astype(np.complex128),
                        verify_args=True,
                    )
        with self.subTest("invalid_gt_values"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.align_shift_scale(
                        mask=self.mask,
                        control_mask=None,
                        gt_values=self.gt_values.astype(np.complex128),
                        pred_values=self.pred_values,
                        verify_args=True,
                    )
        with self.subTest("invalid_mask"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.align_shift_scale(
                        mask=self.mask.astype(np.complex128),
                        control_mask=None,
                        gt_values=self.gt_values,
                        pred_values=self.pred_values,
                        verify_args=True,
                    )
        with self.subTest("invalid_control_mask"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.align_shift_scale(
                        mask=self.mask,
                        control_mask=self.mask.astype(np.complex128),
                        gt_values=self.gt_values,
                        pred_values=self.pred_values,
                        verify_args=True,
                    )

    def test_align_shift_scale__invalid_dtype_pt(self):
        with self.subTest("invalid_pred_values"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(
                            self.pred_values.astype(np.complex128)
                        ),
                        verify_args=True,
                    )
        with self.subTest("invalid_gt_values"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(
                            self.gt_values.astype(np.complex128)
                        ),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_mask"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask.astype(np.complex128)),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_control_mask"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=torch.from_numpy(self.mask.astype(np.complex128)),
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )

    def test_align_shift_scale__inconsistent_shape(self):
        with self.subTest("invalid_gt_values_width"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.double_width(self.gt_values)),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_gt_values_height"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.double_height(self.gt_values)),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_mask_width"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.double_width(self.mask)),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_mask_height"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.double_height(self.mask)),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_control_mask_width"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=torch.from_numpy(self.double_width(self.mask)),
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_control_mask_height"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=torch.from_numpy(self.double_height(self.mask)),
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )

    def test_align_shift_scale__inconsistent_shape_pt(self):
        with self.subTest("invalid_gt_values_width"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.double_width(self.gt_values)),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_gt_values_height"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.double_height(self.gt_values)),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_mask_width"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.double_width(self.mask)),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_mask_height"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.double_height(self.mask)),
                        control_mask=None,
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_control_mask_width"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=torch.from_numpy(self.double_width(self.mask)),
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )
        with self.subTest("invalid_control_mask_height"):
            with self.assertNoLogs():
                with self.assertRaises(ValueError):
                    depth_tools.pt.align_shift_scale(
                        mask=torch.from_numpy(self.mask),
                        control_mask=torch.from_numpy(self.double_height(self.mask)),
                        gt_values=torch.from_numpy(self.gt_values),
                        pred_values=torch.from_numpy(self.pred_values),
                        verify_args=True,
                    )

    def test_align_shift_scale__inconsistent_dtype(self):
        with self.assertNoLogs():
            with self.assertRaises(ValueError):
                depth_tools.align_shift_scale(
                    control_mask=None,
                    gt_values=self.gt_values.astype(np.float64),
                    pred_values=self.pred_values.astype(np.float32),
                    mask=self.mask,
                    verify_args=True,
                )

    def test_align_shift_scale__inconsistent_dtype_pt(self):
        with self.assertNoLogs():
            with self.assertRaises(ValueError):
                depth_tools.pt.align_shift_scale(
                    control_mask=None,
                    gt_values=torch.from_numpy(self.gt_values.astype(np.float64)),
                    pred_values=torch.from_numpy(self.pred_values.astype(np.float32)),
                    mask=torch.from_numpy(self.mask),
                    verify_args=True,
                )

    def test_algin_shift_scale__no_pixel_selected(self):
        with self.assertLogs(level="WARNING"):
            aligned_depth, shift, scale = depth_tools.align_shift_scale(
                control_mask=np.full(self.gt_values.shape, False),
                gt_values=self.gt_values,
                pred_values=self.pred_values,
                mask=self.mask,
                verify_args=True,
            )

        expected_aligned_depth = np.full(
            aligned_depth.shape, np.nan, aligned_depth.dtype
        )

        self.assertArrayEqual(aligned_depth, expected_aligned_depth, equal_nan=True)
        self.assertTrue(math.isnan(shift))
        self.assertTrue(math.isnan(scale))

    def test_algin_shift_scale__no_pixel_selected_pt(self):
        with self.assertLogs(level="WARNING"):
            with torch.no_grad():
                aligned_depth, shift, scale = depth_tools.pt.align_shift_scale(
                    control_mask=torch.from_numpy(np.full(self.gt_values.shape, False)),
                    gt_values=torch.from_numpy(self.gt_values),
                    pred_values=torch.from_numpy(self.pred_values),
                    mask=torch.from_numpy(self.mask),
                    verify_args=True,
                )
        aligned_depth = aligned_depth.numpy()
        shift = shift.item()
        scale = scale.item()

        expected_aligned_depth = np.full(
            aligned_depth.shape, np.nan, aligned_depth.dtype
        )

        self.assertArrayEqual(aligned_depth, expected_aligned_depth, equal_nan=True)
        self.assertTrue(math.isnan(shift))
        self.assertTrue(math.isnan(scale))

    def double_width(self, im: np.ndarray) -> np.ndarray:
        return np.concatenate([im, im], axis=-1)

    def double_height(self, im: np.ndarray) -> np.ndarray:
        return np.concatenate([im, im], axis=-2)
