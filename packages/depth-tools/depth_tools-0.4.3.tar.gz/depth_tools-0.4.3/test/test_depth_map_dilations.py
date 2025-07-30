import unittest
from typing import Any

import npy_unittest
import numpy as np
import torch
from matplotlib import pyplot as plt

import depth_tools
import depth_tools.pt
from depth_tools._depth_map_dilation import (
    _draw_axis_aligned_cube_front_faces_lh_yup_unchecked,
    _get_sphere_dz_map_unchecked,
)


class TestDepthMapDilation(npy_unittest.NpyTestCase):
    def test_fast_dilate_depth_map__happy_path(self):
        base_depth = 10
        point_1_depth = 7
        point_2_depth = 5
        depth_map = np.full((1, 100, 200), 10, dtype=np.float32)
        depth_map[:, 12, 150] = point_1_depth
        depth_map[:, 50, 60] = point_2_depth

        depth_mask = np.full(depth_map.shape, True)

        intrinsics = depth_tools.CameraIntrinsics(f_x=140, f_y=100, c_x=120, c_y=60)
        r = 1

        dilated_depth_map = depth_tools.fast_dilate_depth_map(
            r=r,
            depth_map=depth_map,
            depth_mask=depth_mask,
            intrinsics=intrinsics,
        )

        # check shape and dtype
        self.assertEqual(dilated_depth_map.shape, depth_map.shape)
        self.assertIssubdtype(dilated_depth_map.dtype, np.floating)

        # plt.imshow(dilated_depth_map[0])
        # plt.show(block=True)
        # plt.close()

        # check if all values belong to the proper cubes
        val_map = (
            self.select_pixels(base_depth - r, dilated_depth_map, depth_mask)
            | self.select_pixels(point_1_depth - r, dilated_depth_map, depth_mask)
            | self.select_pixels(point_2_depth - r, dilated_depth_map, depth_mask)
        )

        self.assertAll(val_map)

        # check if all levels are drawn
        self.assertAny(
            self.select_pixels(base_depth - r, dilated_depth_map, depth_mask)
        )
        self.assertAny(
            self.select_pixels(point_1_depth - r, dilated_depth_map, depth_mask)
        )
        self.assertAny(
            self.select_pixels(point_2_depth - r, dilated_depth_map, depth_mask)
        )

        # check if the front AABB has proper size
        front_cube_mask = self.select_pixels(
            point_2_depth - r, dilated_depth_map, depth_mask
        )

        front_cube_depth = point_2_depth - r

        front_cube_start_x, front_cube_start_y, front_cube_end_x, front_cube_end_y = (
            self.get_min_max_trues(front_cube_mask)
        )

        self.assertAlmostEqual(
            front_cube_end_x - front_cube_start_x,
            2 * r / front_cube_depth * intrinsics.f_x,
            delta=1,
        )
        self.assertAlmostEqual(
            front_cube_end_y - front_cube_start_y,
            2 * r / front_cube_depth * intrinsics.f_y,
            delta=1,
        )

        # check if the front AABB front face is not occluded by an AABB front face behind
        self.assertAlmostEqual(
            dilated_depth_map[
                0,
                front_cube_start_y:front_cube_end_y,
                front_cube_start_x:front_cube_end_x,
            ].max(),
            front_cube_depth,
        )

        # check if the AABB front face center is correct
        expected_center_im = self.reproject_point_moved(
            x_im=60,
            y_im=100 - 50,
            camera=intrinsics,
            dz=r,
            pt_depth=point_2_depth,
        )
        actual_center = self.get_mask_center(front_cube_mask)

        self.assertAlmostEqual(expected_center_im[0], actual_center[0], delta=1)
        self.assertAlmostEqual(expected_center_im[1], 100 - actual_center[1], delta=1)

    def test_fast_dilate_depth_map__mask_respected(self):
        depth_map = np.full((1, 200, 200), 10, dtype=np.float32)
        depth_mask = np.full(depth_map.shape, True)

        r = 3

        depth_map[:, :110, :30] = 0
        depth_map[:, :110, 32:] = 100

        depth_mask[:, :110] = False

        intrinsics = depth_tools.CameraIntrinsics(f_x=140, f_y=100, c_x=120, c_y=60)

        dilation_result = depth_tools.fast_dilate_depth_map(
            depth_map=depth_map, depth_mask=depth_mask, intrinsics=intrinsics, r=r
        )

        self.assertAlmostEqual(dilation_result[0, 0, 0].item(), 0)
        self.assertAlmostEqual(dilation_result[0, 0, -1].item(), 0)
        self.assertAlmostEqual(dilation_result[0, -1, -1].item(), 10 - r)

    def test_fast_dilate_depth_map__object_behind_the_camera(self):
        base_depth = 10
        r = 0.1
        point1_depth = r / 2
        depth_map = np.full((1, 100, 200), base_depth, dtype=np.float32)
        depth_map[:, -1, -1] = point1_depth
        depth_mask = np.full(depth_map.shape, True)

        wide_cam = depth_tools.CameraIntrinsics(f_x=14, f_y=10, c_x=120, c_y=60)

        dilated_depth = depth_tools.fast_dilate_depth_map(
            depth_map=depth_map,
            depth_mask=depth_mask,
            intrinsics=wide_cam,
            occlusion_subsampling=None,
            r=r,
        )

        # plt.imshow(depth_map[0])
        # plt.show(block=True)
        # plt.close()

        self.assertLess(float(dilated_depth[:, -1, -1]), point1_depth)
        self.assertAlmostEqual(
            float(dilated_depth[:, -2, -1]), base_depth - r, delta=1e-4
        )

    def test_fast_dilate_depth_map__camera_inside_object(self):
        base_depth = 10
        r = 0.1
        point1_depth = r / 2
        depth_map = np.full((1, 100, 200), base_depth, dtype=np.float32)
        depth_map[:, 50, 40] = point1_depth
        depth_mask = np.full(depth_map.shape, True)

        intrinsics = depth_tools.CameraIntrinsics(f_x=140, f_y=100, c_x=120, c_y=60)

        actual_dilated_depth = depth_tools.fast_dilate_depth_map(
            depth_map=depth_map,
            depth_mask=depth_mask,
            intrinsics=intrinsics,
            occlusion_subsampling=None,
            r=r,
        )

        # plt.imshow(depth_map[0])
        # plt.show(block=True)
        # plt.close()

        expected_dilated_depth = np.zeros_like(actual_dilated_depth)

        self.assertAllclose(actual_dilated_depth, expected_dilated_depth)

    def test_fast_dilate_depth_map__invalid_depth_shape(self) -> None:
        depth = np.full((1, 1, 200, 300), 10, dtype=np.float32)
        mask = np.full((1, 200, 300), True)
        intrinsics = depth_tools.CameraIntrinsics(c_x=150, c_y=100, f_x=100, f_y=100)

        with self.assertRaises(ValueError) as cm:
            depth_tools.fast_dilate_depth_map(
                depth_map=depth,
                depth_mask=mask,
                intrinsics=intrinsics,
                occlusion_subsampling=None,
                r=3,
            )

        self.assertIn("Im_Depth. It does not have exactly 3", str(cm.exception))

    def test_fast_dilate_depth_map__inconsistent_shape(self) -> None:
        depth = np.ones((1, 200, 300), dtype=np.float32)
        mask = np.full((1, 600, 500), True)

        intrinsics = depth_tools.CameraIntrinsics(c_x=150, c_y=100, f_x=100, f_y=100)

        with self.assertRaises(ValueError) as cm:
            depth_tools.fast_dilate_depth_map(
                depth_map=depth,
                depth_mask=mask,
                intrinsics=intrinsics,
                occlusion_subsampling=None,
                r=3,
            )

        self.assertIn("The shape of the depth map", str(cm.exception))

    def test_fast_dilate_depth_map__invalid_dtype(self) -> None:
        depth = np.ones((1, 200, 300), dtype=np.float32)
        mask = np.full(depth.shape, True)

        cases: list[tuple[str, Any, Any, str]] = [
            ("invalid_depth_dtype", np.int32, np.bool_, "The dtype is not floating."),
            ("invalid_mask_dtype", np.float64, np.int32, "The dtype is not bool."),
        ]

        for case_name, depth_dtype, mask_dtype, msg_part in cases:
            with self.subTest(case_name):
                intrinsics = depth_tools.CameraIntrinsics(
                    c_x=150, c_y=100, f_x=100, f_y=100
                )

                with self.assertRaises(ValueError) as cm:
                    depth_tools.fast_dilate_depth_map(
                        depth_map=depth.astype(depth_dtype),
                        depth_mask=mask.astype(mask_dtype),
                        intrinsics=intrinsics,
                        occlusion_subsampling=None,
                        r=3,
                    )

                self.assertIn(msg_part, str(cm.exception))

    def test_fast_dilate_depth_map__negative_r(self) -> None:
        depth = np.ones((1, 200, 300), dtype=np.float32)
        mask = np.full(depth.shape, True)

        intrinsics = depth_tools.CameraIntrinsics(c_x=150, c_y=100, f_x=100, f_y=100)

        with self.assertRaises(ValueError) as cm:
            depth_tools.fast_dilate_depth_map(
                depth_map=depth,
                depth_mask=mask,
                intrinsics=intrinsics,
                occlusion_subsampling=None,
                r=-1,
            )

        self.assertIn("radius of the approximated sphere", str(cm.exception))

    def test_fast_dilate_depth_map__masking(self) -> None:
        depth1 = np.full((1, 300, 400), 10, dtype=np.float32)
        depth2 = np.full((1, 300, 400), 10, dtype=np.float32)
        depth2[:, 150, 200] = 8

        mask = np.full(depth1.shape, True)
        mask[:, 150, 200] = False

        camera = depth_tools.CameraIntrinsics(f_x=100, f_y=100, c_x=200, c_y=150)

        dilated1 = depth_tools.fast_dilate_depth_map(
            r=1, depth_map=depth1, depth_mask=mask, intrinsics=camera
        )
        dilated2 = depth_tools.fast_dilate_depth_map(
            r=1, depth_map=depth2, depth_mask=mask, intrinsics=camera
        )

        self.assertAllclose(dilated1[mask], dilated2[mask])
        self.assertAlmostEqual(dilated2[:, 150, 200], 0, delta=1e-4)

    def test_fast_dilate_depth_map__no_cube(self):
        depth = np.full((1, 300, 400), 10, dtype=np.float32)
        mask = np.full(depth.shape, True)
        intrinsics = depth_tools.CameraIntrinsics(f_x=140, f_y=100, c_x=120, c_y=60)

        depth[:, 50, 70] = 2

        output = depth_tools.fast_dilate_depth_map(
            r=1,
            depth_map=depth,
            depth_mask=mask,
            intrinsics=intrinsics,
            occlusion_subsampling={"max_num": 0},
        )
        output_full = depth_tools.fast_dilate_depth_map(
            r=1,
            depth_map=depth,
            depth_mask=mask,
            intrinsics=intrinsics,
        )

        # plt.imshow(output[0], vmin=0, vmax=10)
        # plt.show(block=True)
        # plt.close()
        # plt.imshow(output_full[0], vmin=0, vmax=10)
        # plt.show(block=True)
        # plt.close()

        self.assertAll(~np.isnan(output))

        output_mean = output[mask].mean()
        output_full_mean = output_full[mask].mean()
        self.assertGreater(output_mean, output_full_mean)
        self.assertGreater(output.max() - output.min(), 0.01)

    def test_fast_dilate_depth_map__1_cube(self):
        depth = np.full((1, 300, 400), 10, dtype=np.float32)
        mask = np.full(depth.shape, True)
        intrinsics = depth_tools.CameraIntrinsics(f_x=140, f_y=100, c_x=120, c_y=60)

        depth[:, 50, 70] = 2

        output = depth_tools.fast_dilate_depth_map(
            r=1,
            depth_map=depth,
            depth_mask=mask,
            intrinsics=intrinsics,
            occlusion_subsampling={"max_num": 1, "rng": np.random.default_rng(304)},
        )
        output_no_cube = depth_tools.fast_dilate_depth_map(
            r=1,
            depth_map=depth,
            depth_mask=mask,
            intrinsics=intrinsics,
            occlusion_subsampling={"max_num": 0},
        )
        self.assertAll(~np.isnan(output))
        self.assertAll(output <= output_no_cube)

    def test_fast_dilate_depth_map__r0(self):
        rng = np.random.default_rng(78)
        depth = rng.uniform(0.01, 100, size=(1, 200, 300))
        mask = np.full(depth.shape, True)
        mask[:, :35] = False

        dilated_depth = depth_tools.fast_dilate_depth_map(
            depth_map=depth,
            depth_mask=mask,
            intrinsics=depth_tools.CameraIntrinsics(f_x=100, f_y=100, c_x=150, c_y=100),
            occlusion_subsampling=None,
            r=0,
        )

        self.assertAllclose(dilated_depth[mask], depth[mask])
        self.assertArrayEqual(dilated_depth[~mask], np.zeros_like(dilated_depth[~mask]))

    def test_draw_axis_aligned_cube_front_faces_lh_yup_unchecked__happy_path(self):
        depth_map = np.full((1, 500, 600), 10, dtype=np.float32)
        depth_map[:, 250, 300] = 2
        depth_mask = np.full(depth_map.shape, True)
        intrinsics = depth_tools.CameraIntrinsics(f_x=100, f_y=100, c_x=300, c_y=250)
        r = 1.5

        depth_const_add = np.full(depth_map.shape, -1, depth_map.dtype)

        resulting_depth = _draw_axis_aligned_cube_front_faces_lh_yup_unchecked(
            cube_centers_vs=np.array([[0, 0, 5], [0, 0, r / 10]], dtype=np.float32),
            r=r,
            depth_map=depth_map,
            depth_mask=depth_mask,
            intrinsics=intrinsics,
            depth_const_add=depth_const_add,
        )

        # plt.imshow(resulting_depth[0])
        # plt.show(block=True)
        # plt.close()

        self.assertEqual(resulting_depth[0, 0, 0], 9)
        self.assertEqual(resulting_depth[0, 250, 300], 1)
        self.assertEqual(resulting_depth[0, 251, 301], 5 - r)

    def test_get_sphere_dz_map_unchecked(self):
        vs_map = np.zeros((3, 2, 2), dtype=np.float32)
        valid_points_mask = np.full((1, 2, 2), True)
        valid_points_mask[:, 1, :] = False

        vs_map[:, 0, 0] = [3, 1, 9]
        vs_map[:, 0, 1] = [0, 0, 5]

        actual_dz_map = _get_sphere_dz_map_unchecked(
            vs_map=vs_map, valid_points_mask=valid_points_mask, r=2
        )
        expected_dz_map = np.array([[[7.1131 - 9, 3 - 5], [0, 0]]], dtype=np.float32)

        self.assertAllclose(actual_dz_map, expected_dz_map, atol=1e-4)

    def get_min_max_trues(self, mask: np.ndarray) -> tuple[int, int, int, int]:
        """
        Calculate the minimal and maximal indices of the true values in the given mask.

        Parameters
        ----------
        mask
            The mask. Format: ``Im_Mask``

        Returns
        -------
        x_min
            The minimal index alongside the X dimension.
        y_min
            The minimal index alongside the Y dimension.
        x_max
            The maximal index alongside the X dimension.
        y_max
            The maximal index alongside the Y dimension.
        """
        mask0: np.ndarray = mask[0]
        y_coords, x_coords = mask0.nonzero()
        x_min = x_coords.min().astype(np.int32).item()
        x_max = x_coords.max().astype(np.int32).item()
        y_min = y_coords.min().astype(np.int32).item()
        y_max = y_coords.max().astype(np.int32).item()

        return x_min, y_min, x_max, y_max

    def get_mask_center(self, mask: np.ndarray) -> tuple[float, float]:
        mask0: np.ndarray = mask[0]
        y_coords, x_coords = mask0.nonzero()

        return x_coords.mean().item(), y_coords.mean().item()

    def select_pixels(
        self, v: float, depth_map: np.ndarray, depth_mask: np.ndarray
    ) -> np.ndarray:
        """
        Select the pixels with the given depth.

        Parameters
        ----------
        depth_map
            The depth map from which the pixels should be selected. Format: ``Im_Depth``
        depth_mask
            The mask that selects the valid pixels from the depth map. Format: ``Im_Mask``

        Returns
        -------
        v
            The mask that selects the valid pixels with the given value. Format: ``Im_Mask``
        """
        return (abs(depth_map - v) < 1e-4) & depth_mask

    def reproject_point_moved(
        self,
        x_im: float,
        y_im: float,
        pt_depth: float,
        dz: float,
        camera: depth_tools.CameraIntrinsics,
    ) -> tuple[float, float]:
        """
        Do a transform on an on-image point.

        Steps:

        1. Take a point in the image space (Y-up) and its corresponding depth.
        2. Calculate the corresponding point in the space, assuming Y-up left handed coordinate system, where the camera looks at the +Z direction.
        3. Move the point with the following vector: ``(0, 0, -dz)``.
        4. Reproject the moved point onto the image.

        Parameters
        ----------
        x_im
            The X coordinate of the point on the image.
        y_im
            The Y coordinate of the point on the image.
        pt_depth
            The depth of the point.
        dz
            The amount of movement.
        camera
            The camera intrinsics.
        """
        x_s = pt_depth * (x_im - camera.c_x) / camera.f_x
        y_s = pt_depth * (y_im - camera.c_y) / camera.f_y

        pt_depth_new = pt_depth - dz

        x_new_im = (x_s * camera.f_x + camera.c_x * pt_depth_new) / pt_depth_new
        y_new_im = (y_s * camera.f_y + camera.c_y * pt_depth_new) / pt_depth_new

        return x_new_im, y_new_im
