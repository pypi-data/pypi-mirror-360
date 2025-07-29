import unittest
from typing import Any

import numpy as np

import depth_tools

from .testutil import TestBase


class TestPointCloud(TestBase):
    def setUp(self):
        self.depth_map = np.array(
            [
                [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9],
                    [10, 11, 12],
                ]
            ],
            dtype=np.float32,
        )
        self.depth_mask = np.array(
            [
                [
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 0],
                    [1, 0, 1],
                ]
            ]
        ).astype(np.bool_)

        self.h_points_for_non_masked_pixels = np.array(
            [
                # top row
                [0, 3, 1],
                [1, 3, 2],
                [2, 3, 3],
                # row below top
                [0, 2, 4],
                [1, 2, 5],
                [2, 2, 6],
                # row above bottom
                [0, 1, 7],
                [1, 1, 8],
                # bottom row
                [0, 0, 10],
                [2, 0, 12],
            ],
            dtype=np.float32,
        )
        self.h_points_for_non_masked_pixels[:, 0] += 0.5
        self.h_points_for_non_masked_pixels[:, 1] += 0.5
        self.h_points_for_non_masked_pixels[:, 0] = (
            self.h_points_for_non_masked_pixels[:, 0]
            * self.h_points_for_non_masked_pixels[:, 2]
        )
        self.h_points_for_non_masked_pixels[:, 1] = (
            self.h_points_for_non_masked_pixels[:, 1]
            * self.h_points_for_non_masked_pixels[:, 2]
        )

        self.image = np.concatenate(
            [self.depth_map * 2.7, self.depth_map * 0.5, self.depth_map * 3.2], axis=0
        )
        self.cam = depth_tools.CameraIntrinsics(c_x=3, c_y=5, f_x=2.7, f_y=9.1)

        color_list_for_rgb_points = []
        for pt in self.h_points_for_non_masked_pixels:
            int_depth = int(pt[2])  # type: ignore
            pt_x = (int_depth - 1) % 3
            pt_y = (int_depth - 1) // 3

            if self.depth_mask[0, pt_y, pt_x]:
                color_list_for_rgb_points.append(self.image[:, pt_y, pt_x])

        self.colors_for_non_masked_px_points = np.array(
            color_list_for_rgb_points, dtype=np.float32
        )

    def _has_h_point_for_non_masked_pixel(self, x: float, y: float, w: float) -> bool:
        h_pt_idx = self._get_h_point_index(x, y, w)
        if h_pt_idx is None:
            return False
        else:
            return True

    def _color_matches_to_h_point(
        self, xyw: tuple[float, float, float], actual_rgb: tuple[float, float, float]
    ) -> bool:
        point_idx = self._get_h_point_index(*xyw)
        expected_rgb_arr = self.colors_for_non_masked_px_points[point_idx]
        actual_rgb_arr = np.array(actual_rgb, dtype=np.float32)
        return np.allclose(expected_rgb_arr, actual_rgb_arr)

    def _get_h_point_index(self, x: float, y: float, w: float) -> int | None:
        pt_arr = np.array([x, y, w], dtype=np.float32)

        for i, r in enumerate(self.h_points_for_non_masked_pixels):
            if np.max(abs(r - pt_arr)) < 0.001:
                return i

        return None

    def test_depth_2_point_cloud__no_image(self):
        for coord_sys in depth_tools.CoordSys:
            with self.subTest(f"{coord_sys=}"):

                actual_point_cloud = depth_tools.depth_2_point_cloud(
                    depth_map=self.depth_map,
                    depth_mask=self.depth_mask,
                    out_coord_sys=coord_sys,
                    intrinsics=self.cam,
                )
                self.assertEqual(actual_point_cloud.shape, (self.depth_mask.sum(), 3))
                self.assertIssubdtype(actual_point_cloud.dtype, np.floating)

                intrinsic_mat = self.cam.get_intrinsic_mat()

                coord_sys_conv_mat = depth_tools.get_coord_sys_conv_mat(
                    from_=coord_sys, to=depth_tools.CoordSys.LH_YUp
                )

                for point_idx in range(len(actual_point_cloud)):
                    actual_point_vec: np.ndarray = actual_point_cloud[[point_idx]].T

                    reprojected_point_vec_h = (
                        intrinsic_mat @ coord_sys_conv_mat @ actual_point_vec
                    )

                    reproj_pt_found = self._has_h_point_for_non_masked_pixel(
                        reprojected_point_vec_h[0, 0],
                        reprojected_point_vec_h[1, 0],
                        reprojected_point_vec_h[2, 0],
                    )

                    self.assertTrue(
                        reproj_pt_found,
                        f"The reprojected homogen point ({reprojected_point_vec_h}) was not found.",
                    )

    def test_depth_2_point_cloud__image(self):
        for coord_sys in depth_tools.CoordSys:
            with self.subTest(f"{coord_sys=}"):
                actual_point_cloud, actual_point_colors = (
                    depth_tools.depth_2_point_cloud(
                        depth_map=self.depth_map,
                        depth_mask=self.depth_mask,
                        out_coord_sys=coord_sys,
                        intrinsics=self.cam,
                        image=self.image,
                    )
                )
                point_cloud_control = depth_tools.depth_2_point_cloud(
                    depth_map=self.depth_map,
                    depth_mask=self.depth_mask,
                    out_coord_sys=coord_sys,
                    intrinsics=self.cam,
                )

                self.assertEqual(actual_point_cloud.shape, (self.depth_mask.sum(), 3))
                self.assertEqual(actual_point_colors.shape, (self.depth_mask.sum(), 3))

                self.assertAllclose(point_cloud_control, actual_point_cloud)
                coord_sys_conv_mat = depth_tools.get_coord_sys_conv_mat(
                    from_=coord_sys, to=depth_tools.CoordSys.LH_YUp
                )
                intrinsic_mat = self.cam.get_intrinsic_mat()

                for point_idx in range(len(actual_point_cloud)):
                    actual_3d_point = actual_point_cloud[[point_idx]].T
                    actual_point_color = actual_point_colors[point_idx]

                    reprojected_point_vec_h = (
                        intrinsic_mat @ coord_sys_conv_mat @ actual_3d_point
                    )
                    color_matches = self._color_matches_to_h_point(
                        xyw=(
                            reprojected_point_vec_h[0, 0],
                            reprojected_point_vec_h[1, 0],
                            reprojected_point_vec_h[2, 0],
                        ),
                        actual_rgb=(
                            actual_point_color[0],
                            actual_point_color[1],
                            actual_point_color[2],
                        ),
                    )
                    self.assertTrue(
                        color_matches,
                        f"Incorrect color for reprojected homogen point {reprojected_point_vec_h}.",
                    )

    def test_depth_2_point_cloud__invalid_inputs(self):
        def input_test(depth, depth_mask, im):
            depth_tools.depth_2_point_cloud(
                depth_map=depth,
                depth_mask=depth_mask,
                out_coord_sys=depth_tools.CoordSys.LH_ZUp,
                intrinsics=self.cam,
                image=im,
            )

        self.probe_invalid_inputs(
            [self.depth_map, self.depth_mask, self.image], input_test
        )

    def test_depths_2_plotly_fig__happy_path(self):
        for expected_fig_title in ["my title", None]:
            with self.subTest(f"{expected_fig_title=}"):
                expected_trace_1_color = "blue"

                expected_trace_1_size = 13
                expected_trace_2_size = 1

                expected_trace_names = [
                    "my_subplot_50",
                    "my_subplot_51",
                    "my_subplot_52",
                    "my_subplot_53",
                ]

                fig = depth_tools.depths_2_plotly_fig(
                    coord_sys=depth_tools.CoordSys.LH_ZUp,
                    depth_maps=[
                        {
                            "color": "blue",
                            "depth_map": self.depth_map,
                            "depth_mask": self.depth_mask,
                            "name": expected_trace_names[0],
                            "size": 13,
                        },
                        {
                            "color": self.image,
                            "depth_map": self.depth_map,
                            "depth_mask": self.depth_mask,
                            "name": expected_trace_names[1],
                            "size": 1,
                        },
                        {
                            "color": self.image,
                            "depth_map": self.depth_map,
                            "depth_mask": self.depth_mask,
                            "name": expected_trace_names[2],
                        },
                        {
                            "depth_map": self.depth_map,
                            "depth_mask": self.depth_mask,
                            "name": expected_trace_names[3],
                        },
                    ],
                    title=expected_fig_title,
                    intrinsics=self.cam,
                )

                data_1_x: Any = fig["data"][0]["x"]  # type: ignore
                data_1_y: Any = fig["data"][0]["y"]  # type: ignore
                data_1_z: Any = fig["data"][0]["z"]  # type: ignore
                data_2_x: Any = fig["data"][1]["x"]  # type: ignore
                data_2_y: Any = fig["data"][1]["y"]  # type: ignore
                data_2_z: Any = fig["data"][1]["z"]  # type: ignore

                expected_n_points = self.depth_mask.sum()

                # data
                self.assertEqual(len(data_1_x), expected_n_points)
                self.assertEqual(len(data_1_y), expected_n_points)
                self.assertEqual(len(data_1_z), expected_n_points)
                self.assertEqual(len(data_2_x), expected_n_points)
                self.assertEqual(len(data_2_y), expected_n_points)
                self.assertEqual(len(data_2_z), expected_n_points)

                # title
                self.assertEqual(fig["layout"]["title"]["text"], expected_fig_title)  # type: ignore

                # marker color
                self.assertIsNotNone(fig["data"][0]["marker"]["color"])  # type: ignore
                self.assertEqual(fig["data"][0]["marker"]["color"], expected_trace_1_color)  # type: ignore

                self.assertIsNotNone(fig["data"][1]["marker"]["color"])  # type: ignore
                self.assertIsInstance(fig["data"][1]["marker"]["color"], np.ndarray)  # type: ignore
                self.assertEqual(fig["data"][1]["marker"]["color"].shape, (expected_n_points, 3))  # type: ignore
                self.assertIsNone(fig["data"][3]["marker"]["color"])  # type: ignore

                # marker size
                self.assertIsNotNone(fig["data"][0]["marker"]["size"])  # type: ignore
                self.assertEqual(fig["data"][0]["marker"]["size"], expected_trace_1_size)  # type: ignore
                self.assertIsNotNone(fig["data"][1]["marker"]["size"])  # type: ignore
                self.assertEqual(fig["data"][1]["marker"]["size"], expected_trace_2_size)  # type: ignore
                self.assertIsNone(fig["data"][2]["marker"]["size"])  # type: ignore

                # name
                for i in range(4):
                    self.assertTrue(fig["data"][i]["showlegend"])  # type: ignore
                    self.assertEqual(fig["data"][i]["name"], expected_trace_names[i])  # type: ignore

                # aspect mode
                actual_aspectmode = fig["layout"]["scene"]["aspectmode"]  # type: ignore
                self.assertEqual(actual_aspectmode, "data")

    def test_depths_2_plotly_fig__camera(self):
        expected_cam_ups: dict[depth_tools.CoordSys, tuple[float, float, float]] = {
            depth_tools.CoordSys.LH_YUp: (0, 1, 0),
            depth_tools.CoordSys.LH_ZUp: (0, 0, 1),
            depth_tools.CoordSys.RH_YUp: (0, 1, 0),
            depth_tools.CoordSys.RH_ZUp: (0, 0, 1),
        }

        expected_mirror_x: dict[depth_tools.CoordSys, bool] = {
            depth_tools.CoordSys.LH_YUp: True,
            depth_tools.CoordSys.LH_ZUp: True,
            depth_tools.CoordSys.RH_YUp: False,
            depth_tools.CoordSys.RH_ZUp: False,
        }

        for coord_sys in depth_tools.CoordSys:
            with self.subTest(f"{coord_sys=}"):
                fig = depth_tools.depths_2_plotly_fig(
                    coord_sys=coord_sys,
                    depth_maps=[
                        {
                            "depth_map": self.depth_map,
                            "depth_mask": self.depth_mask,
                            "name": "trace1",
                        },
                    ],
                    intrinsics=self.cam,
                )
                expected_cam_up_x, expected_cam_up_y, expected_cam_up_z = (
                    expected_cam_ups[coord_sys]
                )

                expected_xaxis_autorange = (
                    "reversed" if expected_mirror_x[coord_sys] else None
                )

                actual_cam_up_x: float | None = fig["layout"]["scene"]["camera"]["up"]["x"]  # type: ignore
                actual_cam_up_y: float | None = fig["layout"]["scene"]["camera"]["up"]["y"]  # type: ignore
                actual_cam_up_z: float | None = fig["layout"]["scene"]["camera"]["up"]["z"]  # type: ignore

                actual_cam_eye_x: float | None = fig["layout"]["scene"]["camera"]["eye"]["x"]  # type: ignore
                actual_cam_eye_y: float | None = fig["layout"]["scene"]["camera"]["eye"]["y"]  # type: ignore
                actual_cam_eye_z: float | None = fig["layout"]["scene"]["camera"]["eye"]["z"]  # type: ignore

                actual_cam_center_x: float | None = fig["layout"]["scene"]["camera"]["center"]["x"]  # type: ignore
                actual_cam_center_y: float | None = fig["layout"]["scene"]["camera"]["center"]["y"]  # type: ignore
                actual_cam_center_z: float | None = fig["layout"]["scene"]["camera"]["center"]["z"]  # type: ignore

                actual_xaxis_autorange: str | bool | None = fig["layout"]["scene"]["xaxis"]["autorange"]  # type: ignore
                actual_yaxis_autorange: str | bool | None = fig["layout"]["scene"]["yaxis"]["autorange"]  # type: ignore
                actual_zaxis_autorange: str | bool | None = fig["layout"]["scene"]["zaxis"]["autorange"]  # type: ignore

                self.assertIsNotNone(actual_cam_up_x)
                self.assertIsNotNone(actual_cam_up_y)
                self.assertIsNotNone(actual_cam_up_z)

                assert actual_cam_up_x is not None
                assert actual_cam_up_y is not None
                assert actual_cam_up_z is not None

                self.assertIsNotNone(actual_cam_eye_x)
                self.assertIsNotNone(actual_cam_eye_y)
                self.assertIsNotNone(actual_cam_eye_z)

                assert actual_cam_eye_x is not None
                assert actual_cam_eye_y is not None
                assert actual_cam_eye_z is not None

                self.assertIsNotNone(actual_cam_center_x)
                self.assertIsNotNone(actual_cam_center_y)
                self.assertIsNotNone(actual_cam_center_z)

                assert actual_cam_center_x is not None
                assert actual_cam_center_y is not None
                assert actual_cam_center_z is not None

                self.assertAlmostEqual(expected_cam_up_x, actual_cam_up_x)
                self.assertAlmostEqual(expected_cam_up_y, actual_cam_up_y)
                self.assertAlmostEqual(expected_cam_up_z, actual_cam_up_z)

                self.assertAlmostEqual(actual_cam_eye_x, 1.25)
                self.assertAlmostEqual(actual_cam_eye_y, 1.25)
                self.assertAlmostEqual(actual_cam_eye_z, 1.25)

                self.assertAlmostEqual(actual_cam_center_x, 0)
                self.assertAlmostEqual(actual_cam_center_y, 0)
                self.assertAlmostEqual(actual_cam_center_z, 0)

                self.assertEqual(actual_xaxis_autorange, expected_xaxis_autorange)
                self.assertEqual(actual_yaxis_autorange, None)
                self.assertEqual(actual_zaxis_autorange, None)

    def test_depths_2_plotly_fig__invalid_arrays(self):
        def fn(depth_map, depth_mask, image):
            depth_tools.depths_2_plotly_fig(
                coord_sys=depth_tools.CoordSys.RH_YUp,
                depth_maps=[
                    {
                        "depth_map": depth_map,
                        "depth_mask": depth_mask,
                        "name": "trace1",
                        "color": image,
                    },
                ],
                intrinsics=self.cam,
            )

        self.probe_invalid_inputs([self.depth_map, self.depth_mask, self.image], fn)
