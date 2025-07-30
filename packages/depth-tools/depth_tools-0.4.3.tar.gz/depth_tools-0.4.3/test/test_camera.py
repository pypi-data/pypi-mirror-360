import unittest

import numpy as np
import numpy.testing

import depth_tools

from .testutil import TestBase


class TestCamera(TestBase):
    def setUp(self):
        self.cam = depth_tools.CameraIntrinsics(c_x=2, c_y=3, f_x=4, f_y=5)

    def test_get_intrinsic_mat(self):
        mat = self.cam.get_intrinsic_mat()

        self.assertIssubdtype(mat.dtype, np.float32)

        self.assertEqual(mat.shape, (3, 3))

        self.assertAlmostEqual(mat[0, 0], self.cam.f_x)
        self.assertAlmostEqual(mat[0, 1], 0)
        self.assertAlmostEqual(mat[0, 2], self.cam.c_x)
        self.assertAlmostEqual(mat[1, 0], 0)
        self.assertAlmostEqual(mat[1, 1], self.cam.f_y)
        self.assertAlmostEqual(mat[1, 2], self.cam.c_y)
        self.assertAlmostEqual(mat[2, 0], 0)
        self.assertAlmostEqual(mat[2, 1], 0)
        self.assertAlmostEqual(mat[2, 2], 1)

    def test_get_intrinsic_mat_inv(self):
        mat = self.cam.get_intrinsic_mat()
        mat_inv = self.cam.get_intrinsic_mat_inv()

        expected_prod = np.eye(3, dtype=np.float32)

        self.assertAllclose(mat @ mat_inv, expected_prod)

    def test_focal_length_validation__x(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.CameraIntrinsics(f_x=-1, f_y=1, c_x=100, c_y=100)

        msg = str(cm.exception)
        self.assertIn("The x focal length should be positive.", msg)
        self.assertIn("-1", msg)

    def test_focal_length_validation__y(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.CameraIntrinsics(f_x=1, f_y=-1, c_x=100, c_y=100)

        msg = str(cm.exception)
        self.assertIn("The y focal length should be positive.", msg)
        self.assertIn("-1", msg)

    def test_from_gl_proj_mat__happy_path(self) -> None:
        P = np.array(
            [
                [2, 0, -3, 0],
                [0, 4, -5, 0],
                [0, 0, -6, 0],
                [0, 0, -1, 0],
            ],
            dtype=np.float32,
        )
        im_width = 300
        im_height = 400

        expected_f_x = P[0, 0] * (im_width - 1) / 2
        expected_f_y = P[1, 1] * (im_height - 1) / 2
        expected_c_x = -P[0, 2] * (im_width - 1) / 2 + (im_width - 1) / 2
        expected_c_y = -P[1, 2] * (im_height - 1) / 2 + (im_height - 1) / 2

        cam = depth_tools.CameraIntrinsics.from_gl_proj_mat(
            P=P, im_width=im_width, im_height=im_height
        )

        self.assertAlmostEqual(cam.f_x, expected_f_x)
        self.assertAlmostEqual(cam.f_y, expected_f_y)
        self.assertAlmostEqual(cam.c_x, expected_c_x)
        self.assertAlmostEqual(cam.c_y, expected_c_y)

    def test_from_gl_proj_mat__negative_fx(self) -> None:
        P = np.array(
            [
                [-1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, -1, 0],
            ],
            dtype=np.float32,
        )
        with self.assertRaises(ValueError) as cm:
            depth_tools.CameraIntrinsics.from_gl_proj_mat(
                P=P, im_width=100, im_height=100
            )
        msg = str(cm.exception)

        self.assertIn("The x focal length should be positive.", msg)

    def test_from_gl_proj_mat__negative_fy(self) -> None:
        P = np.array(
            [
                [1, 0, 0, 0],
                [0, -1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, -1, 0],
            ],
            dtype=np.float32,
        )
        with self.assertRaises(ValueError) as cm:
            depth_tools.CameraIntrinsics.from_gl_proj_mat(
                P=P, im_width=100, im_height=100
            )
        msg = str(cm.exception)

        self.assertIn("The y focal length should be positive.", msg)

    def test_from_gl_proj_mat__negative_width(self) -> None:
        P = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, -1, 0],
            ],
            dtype=np.float32,
        )
        with self.assertRaises(ValueError) as cm:
            depth_tools.CameraIntrinsics.from_gl_proj_mat(
                P=P, im_width=-100, im_height=100
            )
        msg = str(cm.exception)

        self.assertIn("width is non-positive", msg)
        self.assertIn("-100", msg)

    def test_from_gl_proj_mat__negative_height(self) -> None:
        P = np.eye(4, dtype=np.float32)
        with self.assertRaises(ValueError) as cm:
            depth_tools.CameraIntrinsics.from_gl_proj_mat(
                P=P, im_width=100, im_height=-100
            )
        msg = str(cm.exception)

        self.assertIn("height is non-positive", msg)
        self.assertIn("-100", msg)
