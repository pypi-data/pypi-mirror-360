import npy_unittest
import numpy as np
import torch

import depth_tools
import depth_tools.pt


class TestDistMaps(npy_unittest.NpyTestCase):
    def setUp(self):
        self.pos_cam: depth_tools.CameraIntrinsics = depth_tools.CameraIntrinsics(
            f_x=13, f_y=10, c_x=30, c_y=22
        )
        self.depth_maps: np.ndarray = np.zeros((2, 1, 30, 40), dtype=np.float32)

        self.depth_maps[0, :, :10, :15] = 1
        self.depth_maps[0, :, :10, 15:] = 2
        self.depth_maps[0, :, 10:, 15:] = 3
        self.depth_maps[0, :, 10:, :15] = 4
        self.depth_maps[1, :, :10, :15] = 5
        self.depth_maps[1, :, :10, 15:] = 6
        self.depth_maps[1, :, 10:, 15:] = 7
        self.depth_maps[1, :, 10:, :15] = 8

        self.dist_maps: np.ndarray = (
            TestDistMaps._manually_calculate_dist_maps_from_depth_maps_unchecked(
                self.depth_maps, self.pos_cam
            )
        )
        self.neg_cam: depth_tools.CameraIntrinsics = depth_tools.CameraIntrinsics(
            f_x=self.pos_cam.f_x,
            f_y=self.pos_cam.f_y,
            c_x=self.pos_cam.c_x,
            c_y=self.pos_cam.c_y,
        )

    @staticmethod
    def _manually_calculate_dist_maps_from_depth_maps_unchecked(
        depth_maps: np.ndarray, pos_cam: depth_tools.CameraIntrinsics
    ) -> np.ndarray:
        dist_maps: np.ndarray = np.zeros_like(depth_maps)
        p_inv = pos_cam.get_intrinsic_mat_inv()

        map_width = depth_maps.shape[-1]
        map_height = depth_maps.shape[-2]

        for s in range(depth_maps.shape[0]):
            for x_idx in range(map_width):
                for y_idx in range(map_height):
                    x_p = x_idx
                    y_p = map_height - y_idx - 1
                    curr_depth = depth_maps[s, 0, y_idx, x_idx]
                    proj_pt = p_inv @ np.array(
                        [
                            [x_p * curr_depth],
                            [y_p * curr_depth],
                            [curr_depth],
                        ],
                        dtype=np.float32,
                    )

                    x_space = proj_pt[0, 0]
                    y_space = proj_pt[1, 0]
                    z_space = proj_pt[2, 0]
                    dist_maps[s, 0, y_idx, x_idx] = np.sqrt(
                        x_space**2 + y_space**2 + z_space**2
                    )

        return dist_maps

    def test_dist_map_2_depth_map__happy_path__single_im(self) -> None:
        actual_depth_map = depth_tools.dist_map_2_depth_map(
            dist_map=self.dist_maps[0], cam=self.pos_cam, verify_args=True
        )

        self.assertAllclose(actual_depth_map, self.depth_maps[0])

    def test_dist_map_2_depth_map__happy_path__multiple_ims(self) -> None:
        actual_depth_maps = depth_tools.dist_map_2_depth_map(
            dist_map=self.dist_maps, cam=self.pos_cam, verify_args=True
        )

        self.assertAllclose(actual_depth_maps, self.depth_maps)

    def test_dist_map_2_depth_map__invalid_dim_count(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.dist_map_2_depth_map(
                dist_map=self.dist_maps.flatten(), cam=self.pos_cam, verify_args=True
            )

        msg = str(cm.exception)
        self.assertIn(
            "The array containing the given map(s) should have 3 or 4 dimensions", msg
        )

    def test_dist_map_2_depth_map__invalid_channel_count(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.dist_map_2_depth_map(
                dist_map=np.ones((3, 5, 10, 40), dtype=np.float32),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The array containing the given map(s) should have size 1", msg)

    def test_dist_map_2_depth_map__invalid_dtype(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.dist_map_2_depth_map(
                dist_map=self.dist_maps.astype(np.int32),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn(
            "The array containing the given map(s) should contain floating point data",
            msg,
        )

    def test_depth_map_2_dist_map__happy_path__single_im(self):
        actual_dist_map = depth_tools.depth_map_2_dist_map(
            depth_map=self.depth_maps[0], cam=self.pos_cam, verify_args=True
        )

        self.assertAllclose(actual_dist_map, self.dist_maps[0])

    def test_depth_map_2_dist_map__happy_path__multiple_ims(self):
        actual_dist_maps = depth_tools.depth_map_2_dist_map(
            depth_map=self.depth_maps, cam=self.pos_cam, verify_args=True
        )

        self.assertAllclose(actual_dist_maps, self.dist_maps)

    def test_depth_map_2_dist_map__invalid_dim_count(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.depth_map_2_dist_map(
                depth_map=self.depth_maps.flatten(), cam=self.pos_cam, verify_args=True
            )

        msg = str(cm.exception)
        self.assertIn(
            "The array containing the given map(s) should have 3 or 4 dimensions", msg
        )

    def test_depth_map_2_dist_map__invalid_channel_count(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.depth_map_2_dist_map(
                depth_map=np.ones((3, 5, 10, 40), dtype=np.float32),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The array containing the given map(s) should have size 1", msg)

    def test_depth_map_2_dist_map__invalid_dtype(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.dist_map_2_depth_map(
                dist_map=self.depth_maps.astype(np.int32),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn(
            "The array containing the given map(s) should contain floating point data",
            msg,
        )

    def test_dist_map_2_depth_map__happy_path__single_im__pt(self) -> None:
        actual_depth_map = depth_tools.pt.dist_map_2_depth_map(
            dist_map=torch.from_numpy(self.dist_maps[0]),
            cam=self.pos_cam,
            verify_args=True,
        ).numpy()

        self.assertAllclose(actual_depth_map, self.depth_maps[0])

    def test_dist_map_2_depth_map__happy_path__multiple_ims__pt(self) -> None:
        actual_depth_maps = depth_tools.pt.dist_map_2_depth_map(
            dist_map=torch.from_numpy(self.dist_maps),
            cam=self.pos_cam,
            verify_args=True,
        ).numpy()

        self.assertAllclose(actual_depth_maps, self.depth_maps)

    def test_dist_map_2_depth_map__invalid_dim_count__pt(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.dist_map_2_depth_map(
                dist_map=torch.from_numpy(self.dist_maps.flatten()),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn(
            "The array containing the given map(s) should have 3 or 4 dimensions", msg
        )

    def test_dist_map_2_depth_map__invalid_channel_count__pt(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.dist_map_2_depth_map(
                dist_map=torch.ones((3, 5, 10, 40), dtype=torch.float32),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The array containing the given map(s) should have size 1", msg)

    def test_dist_map_2_depth_map__invalid_dtype__pt(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.dist_map_2_depth_map(
                dist_map=torch.from_numpy(self.dist_maps.astype(np.int32)),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn(
            "The array containing the given map(s) should contain floating point data",
            msg,
        )

    def test_depth_map_2_dist_map__happy_path__single_im__pt(self):
        actual_dist_map = depth_tools.pt.depth_map_2_dist_map(
            depth_map=torch.from_numpy(self.depth_maps[0]),
            cam=self.pos_cam,
            verify_args=True,
        ).numpy()

        self.assertAllclose(actual_dist_map, self.dist_maps[0])

    def test_depth_map_2_dist_map__happy_path__multiple_ims__pt(self):
        actual_dist_maps = depth_tools.pt.depth_map_2_dist_map(
            depth_map=torch.from_numpy(self.depth_maps),
            cam=self.pos_cam,
            verify_args=True,
        ).numpy()

        self.assertAllclose(actual_dist_maps, self.dist_maps)

    def test_depth_map_2_dist_map__invalid_dim_count__pt(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.depth_map_2_dist_map(
                depth_map=torch.from_numpy(self.depth_maps.flatten()),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn(
            "The array containing the given map(s) should have 3 or 4 dimensions", msg
        )

    def test_depth_map_2_dist_map__invalid_channel_count__pt(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.depth_map_2_dist_map(
                depth_map=torch.ones((3, 5, 10, 40), dtype=torch.float32),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn("The array containing the given map(s) should have size 1", msg)

    def test_depth_map_2_dist_map__invalid_dtype__pt(self) -> None:
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.depth_map_2_dist_map(
                depth_map=torch.from_numpy(self.depth_maps.astype(np.int32)),
                cam=self.pos_cam,
                verify_args=True,
            )

        msg = str(cm.exception)
        self.assertIn(
            "The array containing the given map(s) should contain floating point data",
            msg,
        )
