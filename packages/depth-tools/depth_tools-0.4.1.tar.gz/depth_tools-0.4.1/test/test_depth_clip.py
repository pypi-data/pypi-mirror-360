import depth_tools
import depth_tools.pt
import npy_unittest
import numpy as np
import torch


class TestDepthClip(npy_unittest.NpyTestCase):
    def test_on_mask__happy_path(self):
        rng = np.random.default_rng(50)
        clip_range = (4, 6)
        clip = depth_tools.DepthClip(clip_range)

        depth = rng.uniform(0.01, 10, size=(1, 60, 75)).astype(np.float32)
        initial_mask = np.full(depth.shape, True)
        initial_mask[:50] = False

        actual_mask = clip.on_mask(mask=initial_mask, gt_depth=depth, verify_args=True)

        expected_mask = initial_mask & (depth > clip_range[0]) & (depth < clip_range[1])

        self.assertArrayEqual(actual_mask, expected_mask)

    def test_on_mask__invalid_shape(self):
        depth = np.ones((1, 54, 60), dtype=np.float32)
        mask = np.full((1, 1, 54, 60), True)

        clip = depth_tools.DepthClip((1, 10))

        with self.assertRaises(ValueError):
            clip.on_mask(mask=mask, gt_depth=depth, verify_args=True)

    def test_on_mask__invalid_dtype(self):
        depth = np.ones((1, 54, 60), dtype=np.float32)
        mask = np.full((1, 1, 54, 60), True)

        dtypes = [
            ("invalid_depth_dtype", np.complex128, np.bool_),
            ("invalid_mask_dtype", np.float32, np.complex128),
        ]

        clip = depth_tools.DepthClip((1, 10))

        for subtest_name, gt_depth_dtype, mask_dtype in dtypes:
            with self.subTest(subtest_name):
                with self.assertRaises(ValueError):
                    clip.on_mask(
                        mask=mask.astype(mask_dtype),
                        gt_depth=depth.astype(gt_depth_dtype),
                        verify_args=True,
                    )

    def test_on_mask__no_clip(self):
        rng = np.random.default_rng(690)
        mask = rng.uniform(0, 1, size=(1, 26, 40)) > 0.5

        depth = np.full((1, 26, 40), 0.001, dtype=np.float32)

        clip = depth_tools.DepthClip(None)

        post_mask = clip.on_mask(gt_depth=depth, mask=mask, verify_args=True)

        self.assertArrayEqual(mask, post_mask)

    def test_init__invalid_args(self):
        with self.assertRaises(ValueError):
            depth_tools.DepthClip((10, 10))

    def test_on_aligned_pred__happy_path(self):
        rng = np.random.default_rng(65)
        clip_range = (4, 6)
        clip = depth_tools.DepthClip(clip_range)

        aligned_pred = rng.uniform(0.01, 10, size=(1, 60, 75)).astype(np.float32)

        actual_out = clip.on_aligned_pred(aligned_pred)
        expected_out = np.clip(aligned_pred, 4, 6)

        self.assertAllclose(actual_out, expected_out)

    def test_on_aligned_pred__invalid_dtype(self):
        depth = np.ones((1, 25, 43), dtype=np.complex128)
        clip = depth_tools.DepthClip((2, 5))

        with self.assertRaises(ValueError):
            clip.on_aligned_pred(depth, verify_args=True)

    def test_on_aligned_pred__no_clip(self):
        depth = np.full((1, 25, 65), 7.6, dtype=np.float32)

        clip = depth_tools.DepthClip(None)

        post_clip = clip.on_aligned_pred(depth)

        self.assertAllclose(depth, post_clip)


class TestDepthClipOnTorch(npy_unittest.NpyTestCase):
    def test_depth_clip_on_aligned_pred(self):
        rng = np.random.default_rng(756)

        depth = rng.uniform(0.1, 10, size=(1, 35, 90)).astype(np.float32)
        clip = depth_tools.DepthClip(clip_range=(2, 9))

        with torch.no_grad():
            actual_result = depth_tools.pt.depth_clip_on_aligned_pred(
                clip=clip, aligned_preds=torch.from_numpy(depth), verify_args=True
            ).numpy()

        expected_result = clip.on_aligned_pred(depth)

        self.assertAllclose(actual_result, expected_result)

    def test_depth_clip_on_aligned_pred__invalid_dtype(self):
        depth = np.ones((1, 25, 43), dtype=np.complex128)
        clip = depth_tools.DepthClip((2, 5))

        with self.assertRaises(ValueError):
            depth_tools.pt.depth_clip_on_aligned_pred(
                clip=clip, aligned_preds=torch.from_numpy(depth), verify_args=True
            )

    def test_depth_clip_on_aligned_pred__no_clip(self):
        depth = np.full((1, 25, 65), 7.6, dtype=np.float32)

        clip = depth_tools.DepthClip(None)

        with torch.no_grad():
            post_clip = depth_tools.pt.depth_clip_on_aligned_pred(
                aligned_preds=torch.from_numpy(depth),
                clip=clip,
            ).numpy()

        self.assertAllclose(depth, post_clip)

    def test_depth_clip_on_mask__happy_path(self):
        mask_dtypes = [np.float32, np.bool]
        for mask_dtype in mask_dtypes:
            with self.subTest(f"{mask_dtype=}"):
                rng = np.random.default_rng(756)

                depth = rng.uniform(0.1, 10, size=(1, 35, 90)).astype(np.float32)
                mask = np.full(depth.shape, True)
                mask[:, :30] = False
                mask = mask.astype(mask_dtype)

                clip = depth_tools.DepthClip(clip_range=(2, 9))

                with torch.no_grad():
                    actual_result = depth_tools.pt.depth_clip_on_mask(
                        mask=torch.from_numpy(mask),
                        clip=clip,
                        gt_depth=torch.from_numpy(depth),
                        verify_args=True,
                    ).numpy()

                expected_result = clip.on_mask(
                    gt_depth=depth, mask=mask, verify_args=True
                )

                self.assertArrayEqual(actual_result, expected_result)

    def test_depth_clip_on_mask__invalid_shape(self):
        clip = depth_tools.DepthClip((1, 10))

        with self.assertRaises(ValueError):
            depth_tools.pt.depth_clip_on_mask(
                clip=clip,
                gt_depth=torch.full((1, 40, 35), 5, dtype=torch.float32),
                mask=torch.full((1, 45, 35), True),
                verify_args=True,
            )

    def test_depth_clip_on_mask__invalid_dtype(self):
        dtypes = [
            ("invalid_depth_dtype", torch.complex128, torch.bool),
            ("invalid_mask_dtype", torch.float32, torch.complex128),
        ]
        shared_shape = (1, 40, 35)

        clip = depth_tools.DepthClip((1, 10))

        for subtest_name, depth_dtype, mask_dtype in dtypes:
            with self.subTest(subtest_name):
                with self.assertRaises(ValueError):
                    depth_tools.pt.depth_clip_on_mask(
                        clip=clip,
                        gt_depth=torch.full(shared_shape, 5, dtype=depth_dtype),
                        mask=torch.full(shared_shape, True, dtype=mask_dtype),
                        verify_args=True,
                    )

    def test_depth_clip_on_mask__no_clip(self):
        rng = np.random.default_rng(690)
        mask = rng.uniform(0, 1, size=(1, 26, 40)) > 0.5

        depth = np.full((1, 26, 40), 0.001, dtype=np.float32)

        with torch.no_grad():
            post_mask = depth_tools.pt.depth_clip_on_mask(
                clip=depth_tools.DepthClip(None),
                gt_depth=torch.from_numpy(depth),
                mask=torch.from_numpy(mask),
                verify_args=True,
            ).numpy()

        self.assertArrayEqual(mask, post_mask)
