import io
import unittest
from collections.abc import Collection, Iterable, Mapping
from pathlib import Path
from typing import Any, Final, Literal, cast

import h5py
import npy_unittest
import numpy as np
import PIL.Image as Image
import scipy.io
from matplotlib import pyplot as plt

import depth_tools


class DatasetTestCase(npy_unittest.NpyTestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self._test_rng = np.random.default_rng()

    def assertCameraOK(self, camera: depth_tools.CameraIntrinsics) -> None:
        self.assertGreater(camera.f_x, 0)
        self.assertGreater(camera.f_y, 0)
        self.assertGreater(camera.c_x, 0)
        self.assertGreater(camera.c_y, 0)

        self.assertAlmostEqual(camera.f_x, camera.f_y, delta=1)
        self.assertDifferent([camera.f_x, camera.c_x, camera.c_y], delta=10)

    def assertNegativeIndexingOK(
        self, dataset: depth_tools.Dataset, non_negative_target_index: int
    ):
        if non_negative_target_index < 0:
            raise ValueError(
                f"Argument non_negative_target_index should be non-negative. Value: {non_negative_target_index}"
            )

        sample = dataset[non_negative_target_index]
        sample_alt = dataset[-len(dataset) + non_negative_target_index]

        self.assertAllclose(sample["rgb"], sample_alt["rgb"])
        self.assertAllclose(sample["depth"], sample_alt["depth"])
        self.assertArrayEqual(sample["mask"], sample_alt["mask"])
        self.assertEqual(sample["name"], sample_alt["name"])

    def assertSupportsIndex(
        self, dataset: depth_tools.Dataset, sample_idx: int
    ) -> None:
        sample_index = dataset[SomethingThatSupportsIndex(sample_idx)]
        sample_int = dataset[sample_idx]

        self.assertAllclose(sample_index["rgb"], sample_int["rgb"])
        self.assertAllclose(sample_index["depth"], sample_int["depth"])
        self.assertArrayEqual(sample_index["mask"], sample_int["mask"])
        self.assertEqual(sample_index["name"], sample_int["name"])
        self.assertEqual(sample_index["camera"], sample_int["camera"])

    def assertDifferent(self, values: Iterable[float], delta: float):
        value_list: list[float] = list(values)

        for i in range(len(value_list)):
            for j in range(len(value_list)):
                if i != j:
                    if abs(value_list[i] - value_list[j]) < delta:
                        raise self.failureException(
                            f"The value {value_list[i]} appears more than once. Other appearance: {value_list[j]}"
                        )

    def generate_random_depths(
        self,
        vmin: float,
        vmax: float,
        width: int,
        height: int,
        n: int,
        custom_values: (
            Mapping[
                tuple[
                    int | Literal[":"],
                    int | Literal[":"],
                    int | Literal[":"],
                    int | Literal[":"],
                ],
                float,
            ]
            | None
        ) = None,
    ) -> np.ndarray:
        """
        Generate random depth maps with the given parameters.

        Parameters
        ----------
        vmin
            The minimal depth value.
        vmax
            The maximal depth value.
        width
            The width of the depth maps.
        height
            The height of the depth maps.
        n
            The number of the depth maps.
        custom_values
            These values are manually set on the otherwise random depth map.

        Returns
        -------
        v
            The final depth maps. Format: ``Ims_Depth``

        Raises
        ------
        ValueError
            If any of the arguments violate the described assumptions.
        """
        if vmin < 0:
            raise ValueError("The minimal depth is negative.")
        if vmax < 0:
            raise ValueError("The maximal depth is negative.")
        if width <= 0:
            raise ValueError("The width of the depth maps is non-positive.")
        if height <= 0:
            raise ValueError("The height of the depth maps is non-positive.")
        if n <= 0:
            raise ValueError("The number of the depth maps is non-positive.")

        depths = self._test_rng.uniform(vmin, vmax, size=(n, 1, height, width)).astype(
            np.float32
        )

        if custom_values is not None:
            for custom_value_idx, custom_value in custom_values.items():
                idx = tuple((slice(None) if v == ":" else v) for v in custom_value_idx)
                depths[idx] = custom_value

        return depths

    def generate_random_masks(
        self, width: int, height: int, n: int, p_true: float
    ) -> np.ndarray:
        """
        Generate random masks with the given parameters.

        The pixel values are generated independently using the Bernoulli distribution.

        Parameters
        ----------
        width
            The width of the masks.
        height
            The height of the masks.
        n
            The number of masks.
        p_true
            The probability of whether a pixel has value true.

        Returns
        -------
        v
            The final masks. Format: ``Ims_Mask``

        Raises
        ------
        ValueError
            If any of the arguments violate the described assumptions.
        """
        if width <= 0:
            raise ValueError("The width of the masks is non-positive.")
        if height <= 0:
            raise ValueError("The height of the masks is non-positive.")
        if n <= 0:
            raise ValueError("The number of masks is non-positive.")
        if not (0 <= p_true <= 1):
            raise ValueError("p(pixel_true) is not in [0, 1].")

        return (
            self._test_rng.uniform(0, 1, size=(n, 1, height, width)).astype(np.float32)
            < p_true
        )

    def generate_random_images(self, width: int, height: int, n: int) -> np.ndarray:
        """
        Generate random RGB images with the given parameters. The channel values are generated with the uniform distribution for each pixel independently.

        Parameters
        ----------
        width
            The width of the images.
        height
            The height of the images.
        n
            The number of images.

        Returns
        -------
        v
            The generated images. Format: ``Ims_RGB``

        Raises
        ------
        ValueError
            If any of the arguments violate the described assumptions.
        """
        if width <= 0:
            raise ValueError("The width of the RGB images is non-positive.")
        if height <= 0:
            raise ValueError("The height of the RGB images is non-positive.")
        if n <= 0:
            raise ValueError("The number of RGB images is non-positive.")

        return self._test_rng.uniform(0, 1, size=(n, 3, height, width)).astype(
            np.float32
        )


class TestHypersim(DatasetTestCase):
    def setUp(self) -> None:
        im_width, im_height = (1024, 768)

        depths = self.generate_random_depths(
            width=im_width, height=im_height, n=2, vmin=0.1, vmax=35
        )
        self.depth0 = cast(np.ndarray, depths[0])
        self.depth1 = cast(np.ndarray, depths[1])

        masks = self.generate_random_masks(
            width=im_width, height=im_height, n=2, p_true=0.7
        )
        self.mask0 = cast(np.ndarray, masks[0])
        self.mask1 = cast(np.ndarray, masks[1])

        rgbs = self.generate_random_images(width=im_width, height=im_height, n=2)
        self.rgb0 = rgbs[0]
        self.rgb1 = rgbs[1]

        self.files = {
            str(
                Path(
                    "./ai_001_001/images/scene_cam_00_geometry_hdf5/frame.0000.depth_meters.hdf5"
                )
            ): self.to_hdf5_geometry(depth=self.depth0, mask=self.mask0),
            str(
                Path(
                    "./ai_001_010/images/scene_cam_00_geometry_hdf5/frame.0001.depth_meters.hdf5"
                )
            ): self.to_hdf5_geometry(depth=self.depth1, mask=self.mask1),
            str(
                Path(
                    "./ai_001_001/images/scene_cam_00_final_preview/frame.0000.tonemap.jpg"
                )
            ): self.to_jpeg_image(self.rgb0),
            str(
                Path(
                    "./ai_001_010/images/scene_cam_00_final_preview/frame.0001.tonemap.jpg"
                )
            ): self.to_jpeg_image(self.rgb1),
        }

        self.train_dataset = depth_tools.SimplifiedHypersimDataset(
            hypersim_dir=".",
            split="train",
            tonemap="jpeg",
            virtual_files=self.virtual_io,
        )
        self.test_dataset = depth_tools.SimplifiedHypersimDataset(
            hypersim_dir=".",
            split="test",
            tonemap="jpeg",
            virtual_files=self.virtual_io,
        )

    def to_hdf5_geometry(self, depth: np.ndarray, mask: np.ndarray) -> bytes:
        binary_io = io.BytesIO()
        with h5py.File(binary_io, mode="w") as f:
            dataset_data = self.depth_2_hypersim_dataset_data_unchecked(
                depth=depth, mask=mask
            )
            f.create_dataset("dataset", data=dataset_data)

        return binary_io.getvalue()

    def depth_2_hypersim_dataset_data_unchecked(
        self, depth: np.ndarray, mask: np.ndarray
    ) -> np.ndarray:
        if (len(depth.shape) != 3) or (depth.shape[0] != 1):
            raise ValueError("The given array does not contain a depth map.")
        if not np.issubdtype(depth.dtype, np.floating):
            raise ValueError("The given array does not contain a depth map.")

        if (len(mask.shape) != 3) or (mask.shape[0] != 1):
            raise ValueError("The given array does not contain an image mask.")
        if not np.issubdtype(mask.dtype, np.bool_):
            raise ValueError("The given array does not contain an image mask.")

        depth = depth.copy().astype(np.float64)

        fltFocal = 886.81
        _, intHeight, intWidth = depth.shape

        x_steps = np.linspace(
            (-0.5 * intWidth) + 0.5, (0.5 * intWidth) - 0.5, intWidth, dtype=np.float32
        )
        y_steps = np.linspace(
            (-0.5 * intHeight) + 0.5,
            (0.5 * intHeight) - 0.5,
            intHeight,
            dtype=np.float32,
        )

        x_vals, y_vals = np.meshgrid(x_steps, y_steps)
        z_vals = np.full([intHeight, intWidth], fltFocal, np.float32)

        xyz_vals = np.stack([x_vals, y_vals, z_vals], axis=0)

        dist_map = (
            np.linalg.norm(xyz_vals, ord=2, axis=0, keepdims=True) * depth / fltFocal
        )

        dist_map[~mask] = np.nan

        return dist_map[0]

    def to_jpeg_image(self, array: np.ndarray) -> bytes:
        if (len(array.shape) != 3) or (array.shape[0] != 3):
            raise ValueError("The given array does not contain an RGB image.")
        if not np.issubdtype(array.dtype, np.floating):
            raise ValueError("The given array does not contain an RGB image.")

        array = (array * 255).astype(np.uint8)
        image = Image.fromarray(array.transpose([1, 2, 0]))

        binary_io = io.BytesIO()
        image.save(binary_io, format="jpeg", quality=100, keep_rgb=True, optimize=False)
        return binary_io.getvalue()

    def virtual_io(self, path: Path) -> bytes:
        return self.files[str(path)]

    def test_len(self) -> None:
        self.assertEqual(len(self.train_dataset), 8791)
        self.assertEqual(len(self.test_dataset), 1695)

    def test_item_name(self) -> None:
        sample0_train = self.train_dataset[0]
        sample1_test = self.test_dataset[1]

        self.assertEqual(sample0_train["name"], "ai_001_001,cam_00,frame.0000")
        self.assertEqual(sample1_test["name"], "ai_001_010,cam_00,frame.0001")

    def test_rgb(self):
        sample0_train = self.train_dataset[0]
        sample1_test = self.test_dataset[1]

        self.assertAllclose(sample0_train["rgb"], self.rgb0, atol=1e-1)
        self.assertAllclose(sample1_test["rgb"], self.rgb1, atol=1e-1)

    def test_depth(self):
        sample0_train = self.train_dataset[0]
        sample1_test = self.test_dataset[1]

        expected_train_depth = self.depth0.copy()
        expected_train_depth[~self.mask0] = 0

        expected_test_depth = self.depth1.copy()
        expected_test_depth[~self.mask1] = 0

        self.assertAllclose(
            sample0_train["depth"], expected_train_depth, equal_nan=True, atol=1e-4
        )
        self.assertAllclose(
            sample1_test["depth"], expected_test_depth, equal_nan=True, atol=1e-4
        )

    def test_camera(self):
        sample0_train = self.train_dataset[0]
        sample1_test = self.test_dataset[1]
        self.assertCameraOK(sample0_train["camera"])
        self.assertCameraOK(sample1_test["camera"])

    def test_supports_index(self):
        self.assertSupportsIndex(self.test_dataset, 1)

    def test_negative_indexing(self):
        self.assertNegativeIndexingOK(self.test_dataset, 1)


class TestNyuv2(DatasetTestCase):
    def setUp(self) -> None:
        self.train_indices = [0, 2, 6]
        self.test_indices = [1, 3, 4, 5]
        self.scene_types = [
            "kitchen",
            "office",
            "bus",
            "store",
            "classroom",
            "school",
            "laboratory",
        ]

        self.n_images = 7
        self.im_width = 640
        self.im_height = 480

        self.rgbs = self.generate_random_images(
            width=self.im_width, height=self.im_height, n=self.n_images
        )

        self.depths = self.generate_random_depths(
            vmin=depth_tools.Nyuv2Dataset.MIN_DEPTH_EVAL + 0.0001,
            vmax=depth_tools.Nyuv2Dataset.NYUV2_MAX_DEPTH - 0.0001,
            width=self.im_width,
            height=self.im_height,
            n=self.n_images,
            custom_values={
                (
                    ":",
                    0,
                    self.im_height // 2,
                    self.im_width // 2,
                ): depth_tools.Nyuv2Dataset.NYUV2_MAX_DEPTH
                * 5,
                (
                    ":",
                    0,
                    self.im_height // 2 + 1,
                    self.im_width // 2 + 2,
                ): depth_tools.Nyuv2Dataset.MIN_DEPTH_EVAL
                / 3,
            },
        )

        self.masks = self.generate_random_masks(
            width=self.im_width, height=self.im_height, n=self.n_images, p_true=0.9
        )

        splits_bytes = self.generate_mat_from_splits(
            train_indices=self.train_indices, test_indices=self.test_indices
        )
        samples_hdf5 = self.generate_hdf5_from_samples(
            rgbs=self.rgbs,
            depths=self.depths,
            masks=self.masks,
            scene_types=self.scene_types,
        )

        self.samples_hdf5 = samples_hdf5

        self.train_dataset = depth_tools.Nyuv2Dataset(
            dataset_dir=".",
            add_black_frame=True,
            split="train",
            virtual_files={
                "splits": splits_bytes,
                "nyu_depth_v2_labeled": samples_hdf5,
            },
        )
        self.test_dataset = depth_tools.Nyuv2Dataset(
            dataset_dir=".",
            add_black_frame=True,
            split="test",
            virtual_files={
                "splits": splits_bytes,
                "nyu_depth_v2_labeled": samples_hdf5,
            },
        )

    def tearDown(self) -> None:
        self.samples_hdf5.close()

    def generate_mat_from_splits(
        self, train_indices: Iterable[int], test_indices: Iterable[int]
    ) -> bytes:
        """
        Generate a mat file with the same structure as `split.mat`.

        Parameters
        ----------
        train_indices
            The zero-based indices of the training samples. The function internally converts them to one-based indices.
        test_indices
            The zero-based indices of the test samples. The function internally converts them to one-based indices.

        Returns
        -------
        v
            The binary data for the mat file.

        Raises
        ------
        ValueError
            If any of the indices is negative.
        """
        if any(idx < 0 for idx in train_indices):
            raise ValueError(
                f"The training indices should be non-negative. Training indices: {train_indices}"
            )

        if any(idx < 0 for idx in test_indices):
            raise ValueError(
                f"The test indices should be non-negative. Training indices: {test_indices}"
            )

        stream = io.BytesIO()
        scipy.io.savemat(
            stream,
            {
                "trainNdxs": np.array([[idx + 1] for idx in train_indices]),
                "testNdxs": np.array([[idx + 1] for idx in test_indices]),
            },
        )
        return stream.getvalue()

    def generate_hdf5_from_samples(
        self,
        rgbs: np.ndarray,
        depths: np.ndarray,
        masks: np.ndarray,
        scene_types: Collection[str],
    ) -> h5py.File:
        """
        Generate a NYU Depth v2-like hdf5 file from the given images, depths and masks.

        Parameters
        ----------
        rgbs
            The images. Format: ``Ims_RGB``
        depths
            The depth maps. Format: ``Ims_Depth``
        masks
            The masks. Format: ``Ims_Mask``
        scene_dtypes
            The scene type for each scene.

        Returns
        -------
        v
            The generated hdf5 file.
        """
        if (len(rgbs.shape) != 4) or (rgbs.shape[1] != 3):
            raise ValueError("The rgb image array does not contain RGB images.")
        if not np.issubdtype(rgbs.dtype, np.floating):
            raise ValueError("The rgb image array does not contain RGB images.")

        if (len(depths.shape) != 4) or (depths.shape[1] != 1):
            raise ValueError("The depth map array does not contain depth maps.")
        if not np.issubdtype(depths.dtype, np.floating):
            raise ValueError("The depth map array does not contain depth maps.")

        if (len(masks.shape) != 4) or (masks.shape[1] != 1):
            raise ValueError("The mask array does not contain masks.")
        if not np.issubdtype(masks.dtype, np.bool_):
            raise ValueError("The mask array does not contain masks.")

        if self.slice_shape(rgbs, [0, 2, 3]) != self.slice_shape(depths, [0, 2, 3]):
            raise ValueError(
                "The number of elements, width or height in the RGB image array are not equal to the corresponding dimensions in the depth map array."
            )

        if self.slice_shape(rgbs, [0, 2, 3]) != self.slice_shape(masks, [0, 2, 3]):
            raise ValueError(
                "The number of elements, width or height in the RGB image array are not equal to the corresponding dimensions in the mask array."
            )

        _, _, im_width, im_height = rgbs.shape
        expected_im_width = 640
        expected_im_height = 480
        if (im_width, im_height) == (expected_im_width, expected_im_height):
            raise ValueError(
                f"The size of the individual images is (w={im_width}, h={im_height}) instead of (w={expected_im_width}, h={expected_im_height})"
            )

        depths = depths.copy()
        depths[~masks] = 0

        storage = io.BytesIO()
        samples_file = h5py.File(storage, mode="w")
        samples_file["images"] = (rgbs * 255).astype(np.uint8).transpose([0, 1, 3, 2])
        samples_file["rawDepths"] = depths.squeeze(1).transpose([0, 2, 1])

        string_writer = HDF5StringWriter(samples_file)
        string_writer.write_str_array("sceneTypes", scene_types)
        samples_file.flush()

        return samples_file

    def slice_shape(self, arr: np.ndarray, items: Iterable[int]) -> list[int]:
        return [int(arr.shape[idx]) for idx in items]

    def test_len(self) -> None:
        self.assertEqual(len(self.train_dataset), len(self.train_indices))
        self.assertEqual(len(self.test_dataset), len(self.test_indices))

    def test_add_black_frame(self) -> None:
        self.assertTrue(self.train_dataset.add_black_frame)
        self.assertTrue(self.test_dataset.add_black_frame)

    def test_item_name(self) -> None:
        sample0_train = self.train_dataset[0]
        sample1_test = self.test_dataset[1]

        split_im_idx_train = self.train_indices[0]
        split_im_idx_test = self.test_indices[1]

        self.assertEqual(
            sample0_train["name"],
            f"train/{self.scene_types[self.train_indices[0]]}/rgb_0000{split_im_idx_train}.jpg",
        )
        self.assertEqual(
            sample1_test["name"],
            f"test/{self.scene_types[self.test_indices[1]]}/rgb_0000{split_im_idx_test}.jpg",
        )

    def test_rgb(self):
        sample0_train = self.train_dataset[0]
        sample1_test = self.test_dataset[1]

        border_index = (slice(None), slice(7, 474), slice(7, 632))

        expected_rgb_train = np.zeros(
            (3, self.im_height, self.im_width), dtype=np.float32
        )
        expected_rgb_train[border_index] = self.rgbs[self.train_indices[0]][
            border_index
        ]

        expected_rgb_test = np.zeros(
            (3, self.im_height, self.im_width), dtype=np.float32
        )
        expected_rgb_test[border_index] = self.rgbs[self.test_indices[1]][border_index]

        self.assertAllclose(sample0_train["rgb"], expected_rgb_train, atol=1e-1)
        self.assertAllclose(sample1_test["rgb"], expected_rgb_test, atol=1e-1)

    def test_depth(self):
        sample0_train = self.train_dataset[0]
        sample1_test = self.test_dataset[1]

        frame_inside_slice = (slice(None), slice(45, 471), slice(41, 601))

        expected_train_depth = np.zeros(
            (1, self.im_height, self.im_width), dtype=np.float32
        )
        expected_train_mask = self.masks[self.train_indices[0]]
        expected_train_depth[frame_inside_slice] = self.depths[self.train_indices[0]][
            frame_inside_slice
        ].copy()
        expected_train_depth[~expected_train_mask] = 0
        expected_train_depth[
            (expected_train_depth > depth_tools.Nyuv2Dataset.NYUV2_MAX_DEPTH)
            | (expected_train_depth < depth_tools.Nyuv2Dataset.MIN_DEPTH_EVAL)
        ] = 0

        expected_test_mask = self.masks[self.test_indices[1]]
        expected_test_depth = np.zeros(
            (1, self.im_height, self.im_width), dtype=np.float32
        )
        expected_test_depth[frame_inside_slice] = self.depths[self.test_indices[1]][
            frame_inside_slice
        ].copy()
        expected_test_depth[~expected_test_mask] = 0
        expected_test_depth[
            expected_test_depth > depth_tools.Nyuv2Dataset.NYUV2_MAX_DEPTH
        ] = 0
        expected_test_depth[
            expected_test_depth < depth_tools.Nyuv2Dataset.MIN_DEPTH_EVAL
        ] = 0

        self.assertAllclose(sample0_train["depth"], expected_train_depth)
        self.assertAllclose(sample1_test["depth"], expected_test_depth)

    def test_mask(self):
        sample0_train = self.train_dataset[0]
        sample1_test = self.test_dataset[1]

        depth_train = sample0_train["depth"]
        expected_mask_train: np.ndarray = self.masks[self.train_indices[0]].copy()
        expected_mask_train[45:471, 41:601] = False
        expected_mask_train = (
            expected_mask_train
            & (depth_train > depth_tools.Nyuv2Dataset.MIN_DEPTH_EVAL)
            & (depth_train < depth_tools.Nyuv2Dataset.NYUV2_MAX_DEPTH)
        )

        depth_test = sample1_test["depth"]
        expected_mask_test: np.ndarray = self.masks[self.test_indices[1]].copy()
        expected_mask_test[45:471, 41:601] = False
        expected_mask_test = (
            expected_mask_test
            & (depth_test > depth_tools.Nyuv2Dataset.MIN_DEPTH_EVAL)
            & (depth_test < depth_tools.Nyuv2Dataset.NYUV2_MAX_DEPTH)
        )

        self.assertArrayEqual(sample0_train["mask"], expected_mask_train)
        self.assertArrayEqual(sample1_test["mask"], expected_mask_test)

    def test_camera(self):
        sample0 = self.train_dataset[0]
        self.assertCameraOK(sample0["camera"])

    def test_supports_index(self):
        self.assertSupportsIndex(self.train_dataset, 1)
        self.assertSupportsIndex(self.test_dataset, 0)

    def test_negative_indexing(self):
        self.assertNegativeIndexingOK(self.train_dataset, 1)


class HDF5StringWriter:
    def __init__(self, hdf5_file: h5py.File, refs_group_name: str = "#refs#") -> None:
        self._hdf5_file = hdf5_file
        self._refs_group = self._hdf5_file.create_group(refs_group_name)
        self._counter = 0

    def write_str_array(self, new_dataset_name: str, values: Collection[str]) -> None:
        new_dataset = self._hdf5_file.create_dataset(
            new_dataset_name, shape=(1, len(values)), dtype=h5py.ref_dtype
        )
        for i, value in enumerate(values):
            dataset_ref = self.write_str(value)
            new_dataset[0, i] = dataset_ref

    def write_str(self, value: str) -> Any:
        arr = np.array([[ord(c)] for c in value])
        new_dataset = self._refs_group.create_dataset(
            f"str_{self._counter}", dtype="<u2", data=arr
        )
        self._counter += 1
        return new_dataset.ref


class SomethingThatSupportsIndex:
    def __init__(self, value: int):
        self.value: Final = value

    def __index__(self) -> int:
        return self.value
