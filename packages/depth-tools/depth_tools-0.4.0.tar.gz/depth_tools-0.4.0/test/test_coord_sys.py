import itertools
import unittest

import depth_tools
import numpy as np

from .testutil import TestBase


class TestCoordSys(TestBase):
    def test_get_coord_sys_conv_mat(self):
        x_dir = np.array(
            [
                [1],
                [0],
                [0],
            ],
            dtype=np.float32,
        )
        y_dir = np.array(
            [
                [0],
                [1],
                [0],
            ],
            dtype=np.float32,
        )
        z_dir = np.array(
            [
                [0],
                [0],
                [1],
            ],
            dtype=np.float32,
        )
        forward_dirs = {
            depth_tools.CoordSys.LH_YUp: z_dir,
            depth_tools.CoordSys.LH_ZUp: -y_dir,
            depth_tools.CoordSys.RH_YUp: -z_dir,
            depth_tools.CoordSys.RH_ZUp: y_dir,
        }
        up_dirs = {
            depth_tools.CoordSys.LH_YUp: y_dir,
            depth_tools.CoordSys.LH_ZUp: z_dir,
            depth_tools.CoordSys.RH_YUp: y_dir,
            depth_tools.CoordSys.RH_ZUp: z_dir,
        }

        for src_cs, dst_cs in itertools.product(
            depth_tools.CoordSys, depth_tools.CoordSys
        ):
            with self.subTest(f"{src_cs=};{dst_cs=}"):
                start_right_dir = x_dir
                start_forward_dir = forward_dirs[src_cs]
                start_up_dir = up_dirs[src_cs]

                conv_mat = depth_tools.get_coord_sys_conv_mat(from_=src_cs, to=dst_cs)

                actual_dest_right_dir = conv_mat @ start_right_dir
                actual_dest_forward_dir = conv_mat @ start_forward_dir
                actual_dest_up_dir = conv_mat @ start_up_dir

                expected_dest_right_dir = x_dir
                expected_dest_forward_dir = forward_dirs[dst_cs]
                expected_dest_up_dir = up_dirs[dst_cs]

                if (
                    src_cs == depth_tools.CoordSys.RH_ZUp
                    and dst_cs == depth_tools.CoordSys.LH_ZUp
                ):
                    a = 2

                self.assertAllclose(actual_dest_right_dir, expected_dest_right_dir)
                self.assertAllclose(actual_dest_forward_dir, expected_dest_forward_dir)
                self.assertAllclose(actual_dest_up_dir, expected_dest_up_dir)
