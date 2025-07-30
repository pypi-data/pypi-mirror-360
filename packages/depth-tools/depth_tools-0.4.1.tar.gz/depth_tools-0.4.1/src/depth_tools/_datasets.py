import io
import re
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Literal,
    Protocol,
    SupportsIndex,
    TypedDict,
    cast,
)

import numpy as np
from matplotlib import pyplot as plt
from typing_extensions import Self

from ._camera import CameraIntrinsics
from ._nyuv2_util_internal import (
    decode_nyuv2_hdf5_str_list_unchecked,
    decode_nyuv2_split_idx_list_unchecked,
)

if TYPE_CHECKING:
    import h5py


class Sample(TypedDict):
    name: str
    rgb: np.ndarray
    depth: np.ndarray
    camera: CameraIntrinsics
    mask: np.ndarray


class Dataset(Protocol):
    def __len__(self) -> int: ...

    def __getitem__(self, index: SupportsIndex, /) -> "Sample": ...

    def __iter__(self) -> Iterator[Sample]: ...


class Nyuv2Dataset:
    """
    The class to access the Eigen split of the NyuV2 dataset. The dataset uses the following files:

    * <http://horatio.cs.nyu.edu/mit/silberman/nyu_depth_v2/nyu_depth_v2_labeled.mat>
    * <http://horatio.cs.nyu.edu/mit/silberman/indoor_seg_sup/splits.mat>

    Note that this class opens the hdf5 file of the dataset until the ``Nyuv2Dataset.close`` method is not invoked. You can also use this class with a with statement to close the file automatically.

    Extra dependencies: h5py, scipy

    Parameters
    ----------
    dataset_dir
        The directory containing the dataset.
    add_black_frame
        If true, then a black frame is added to the images that hides the white edges around the images.
    split
        The split to use.
    virtual_files
        Load the dataset files from somewhere else than the disk. In this case, the ``dataset_dir`` will be ignored. It uses the following keys: ``nyu_depth_v2_labeled``: the HDF5 file object that contains the images. It should have the same format as if ``nyu_depth_v2_labeled.mat`` was opened. The class **does close** this file object when ``Nyuv2Dataset.close`` is invoked.  ``splits``: the binary data of the file that contains the splits. It should have the same format as ``splits.mat``.
    """

    MIN_DEPTH_EVAL: Final = 0.001
    NYU_V2_CAM: Final = CameraIntrinsics(f_x=525, f_y=525, c_x=319.5, c_y=239.5)
    NYUV2_MAX_DEPTH: Final = 10

    def __init__(
        self,
        dataset_dir: Path | str,
        add_black_frame: bool,
        split: Literal["train", "test"],
        virtual_files: "_Nyuv2ExplicitFiles | None" = None,
    ):
        import h5py
        import scipy

        if isinstance(dataset_dir, str):
            dataset_dir = Path(dataset_dir)

        labeled_mat_path = dataset_dir / "nyu_depth_v2_labeled.mat"
        splits_mat_path = dataset_dir / "splits.mat"

        if virtual_files is None:
            h5_file = h5py.File(str(labeled_mat_path), "r")
            train_test: np.ndarray = scipy.io.loadmat(str(splits_mat_path))
        else:
            h5_file = virtual_files["nyu_depth_v2_labeled"]
            train_test_io = io.BytesIO(virtual_files["splits"])
            train_test: np.ndarray = scipy.io.loadmat(train_test_io)

        ndx_key = {"test": "testNdxs", "train": "trainNdxs"}[split]
        self._split_im_idxs = decode_nyuv2_split_idx_list_unchecked(train_test[ndx_key])
        self._raw_depths = cast(h5py.Dataset, h5_file["rawDepths"])
        self._images = cast(h5py.Dataset, h5_file["images"])
        self._scenes: list[str] = decode_nyuv2_hdf5_str_list_unchecked(
            h5_file, "sceneTypes"
        )
        self.add_black_frame = add_black_frame
        self.path_start = split
        self._h5_file = h5_file

    def __len__(self) -> int:
        return len(self._split_im_idxs)

    def __getitem__(self, i: SupportsIndex) -> Sample:
        if not self._h5_file.id.valid:
            raise RuntimeError("The hdf5 file backing the dataset is closed.")

        split_im_idx = self._split_im_idxs[i] - 1
        scene_name = (
            f"{self.path_start}/{self._scenes[split_im_idx]}/rgb_{split_im_idx:05d}.jpg"
        )

        rgbs_without_black_boundary: np.ndarray = self._images[split_im_idx].transpose(
            [0, 2, 1]
        )
        if self.add_black_frame:
            rgb = np.zeros_like(rgbs_without_black_boundary, dtype=np.uint8)
            rgb[:, 7:474, 7:632] = rgbs_without_black_boundary[:, 7:474, 7:632]
        else:
            rgb = rgbs_without_black_boundary
        rgb = rgb.astype(np.float32) / 255

        gt_depth = self._raw_depths[split_im_idx]
        gt_depth = np.expand_dims(gt_depth, axis=0)
        gt_depth = gt_depth.transpose([0, 2, 1])

        valid_masks = np.logical_and(
            gt_depth > self.MIN_DEPTH_EVAL, gt_depth < Nyuv2Dataset.NYUV2_MAX_DEPTH
        )

        eval_mask = np.zeros(shape=valid_masks.shape)
        eval_mask[0, 45:471, 41:601] = 1

        total_mask = np.logical_and(valid_masks, eval_mask)
        gt_depth[~total_mask] = 0

        return {
            "name": scene_name,
            "rgb": rgb,
            "depth": gt_depth,
            "mask": total_mask,
            "camera": Nyuv2Dataset.NYU_V2_CAM,
        }

    def __iter__(self) -> Iterator[Sample]:
        for i in range(len(self)):
            yield self[i]

    def close(self):
        self._h5_file.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        self.close()


class _Nyuv2ExplicitFiles(TypedDict):
    nyu_depth_v2_labeled: "h5py.File"
    splits: bytes


class SimplifiedHypersimDataset:
    R"""
    The class to access the hypersim dataset. It requires the presence of the following files from the dataset:

    - ``*.depth_meters.hdf5``
    - ``*.tonemap.jpg`` if tonemap is set to ``jpeg``. Otherwise you may require different files from the dataset, depending on your tonemapping algorithm.

    The class exposes the following data:

    * The depth maps.
    * The images.

    The depth maps produced by the dataset are "true" depth maps and not the distance maps stored in the hdf5 files.

    Since the Hypersim dataset contains HDR images, you can use multiple tonemapping algorithms or load the HDR images directly. If tonemapping is set to ``jpeg``, then it uses the jpeg images provided by the dataset authors. However, you can also specify your own tonemapping algorithm. Keep in mind, that you might need further files from the dataset in this case. The tonemapping function expects the following parameters:

    * ``dataset_dir``: The directory of the dataset.
    * ``ai``: The string that specifies the ai directory. Format: ``ai_\d\d\d_\d\d\d``
    * ``cam``: The string that specifies the cam directory. Format: ``cam_\d\d``
    * ``frame``: The string that specifies the frame to use. Format: ``frame.\d\d\d\d``
    * file_loader: The function to use to load the files. You should use this instead of direct file access to enable the abstraction of the file access.

    Extra dependencies: h5py, Pillow

    Parameters
    ----------
    hypersim_dir
        The directory of the hypersim dataset.
    split
        The split to use.
    tonemap
        The tonemapping algorithm to use. If it is set to ``jpeg``, then it uses the jpeg images provided by the dataset authors. However, you can also specify your own tonemapping algorithm, since Hypersim is a HDR dataset. Keep in mind, that you might need further files from the dataset in this case.
    virtual_files
        Load the dataset files from somewhere else than the disk. The function expects the concatenation of the path of the hypersim dir and the relative file path and gives back the binary data. This function does not affect the split loading, since the this dataset class uses its own split.

    Developer notes
    ---------------
    The split files have a CSV-like format, where each row looks like the following: ``ai_\d\d\d_\d\d\d,cam_\d\d,frame.\d\d\d\d`` each part denotes the corresponding parts in the dataset paths. Note that the lines should contain the ``ai``, ``cam_``, and ``frame.`` texts too.
    """

    def __init__(
        self,
        hypersim_dir: Path | str,
        split: Literal["train", "test", "val"],
        tonemap: 'Literal["jpeg"] | _TonemapFn',
        virtual_files: Callable[[Path], bytes] | None = None,
    ) -> None:
        import h5py
        import PIL.Image as Image

        if isinstance(hypersim_dir, str):
            hypersim_dir = Path(hypersim_dir)

        self._hypersim_dir = hypersim_dir
        """
        The directory of the Hypersim dataset.
        """
        self._split: Literal["train", "test", "val"] = split

        split_path = SimplifiedHypersimDataset._get_split_path(split)

        split_data = SimplifiedHypersimDataset._load_split(split_path)

        self._split_data = split_data

        self._scenes: Final = SimplifiedHypersimDataset._extract_scenes_from_split(
            self._split_data
        )

        self._gl_cam_dict = SimplifiedHypersimDataset._load_camera_intrinsics_dict(
            self._scenes
        )
        """
        The dict that maps the camera parameters for each scene.
        """

        self.tonemap = tonemap

        self._file_type = h5py.File
        self._image_type = Image

        self._file_loader = virtual_files if virtual_files else lambda p: p.read_bytes()

    @property
    def split(self) -> Literal["train", "test", "val"]:
        return self._split

    @property
    def scenes(self) -> frozenset[str]:
        return self._scenes

    @property
    def hypersim_dir(self) -> Path:
        return self._hypersim_dir

    @staticmethod
    def _get_split_path(split: Literal["train", "test", "val"]) -> Path:
        splits_root = Path(__file__).parent / "hypersim_splits"
        match split:
            case "train":
                return splits_root / "train.txt"
            case "test":
                return splits_root / "test.txt"
            case "val":
                return splits_root / "val.txt"

    @staticmethod
    def _load_camera_intrinsics_dict(
        split_scenes: Iterable[str],
    ) -> dict[str, CameraIntrinsics]:
        import pandas as pd

        metadata_csv_path = (
            Path(__file__).parent
            / "hypersim_metadata_original"
            / "camera_parameters.csv"
        )

        frame = pd.read_csv(metadata_csv_path)

        gl_mat_dict: dict[str, CameraIntrinsics] = {}

        for _, f_row in frame.iterrows():
            scene_name = f_row["scene_name"]

            if scene_name not in split_scenes:
                continue

            mat = np.zeros((4, 4), dtype=np.float32)
            for r in range(4):
                for c in range(4):
                    mat[r, c] = f_row[f"M_proj_{r}{c}"]

            im_width = f_row["settings_output_img_width"]
            im_height = f_row["settings_output_img_height"]

            cam = CameraIntrinsics.from_gl_proj_mat(
                P=mat, im_width=im_width, im_height=im_height
            )

            gl_mat_dict[scene_name] = cam

        return gl_mat_dict

    @staticmethod
    def _extract_scenes_from_split(
        split: Iterable[tuple[str, str, str]],
    ) -> frozenset[str]:
        scenes: set[str] = set()
        for sample in split:
            scenes.add(sample[0])
        return frozenset(scenes)

    @staticmethod
    def _load_split(split_path: Path) -> tuple[tuple[str, str, str], ...]:
        R"""
        Load the given split.

        The format of each tuple: ``("ai_\d\d\d_\d\d\d"),("cam_\d\d"),("frame.\d\d\d\d")``
        """
        lines = split_path.read_text().splitlines()
        line_pattern = r"^(ai_\d\d\d_\d\d\d),(cam_\d\d),(frame.\d\d\d\d)$"

        split_items: list[tuple[str, str, str]] = []

        for line in lines:
            line_match = re.match(line_pattern, line)
            if not line_match:
                raise RuntimeError(f'The split line is invalid. Line: "{line}"')
            ai = line_match.group(1)
            cam = line_match.group(2)
            frame = line_match.group(3)

            split_items.append((ai, cam, frame))

        return tuple(split_items)

    def __len__(self):
        return len(self._split_data)

    @staticmethod
    def _dist_2_depth(dist_map: np.ndarray) -> np.ndarray:
        """
        Convert a distance map, used by Hypersim, to depth maps.

        Parameters
        ----------
        dist_map
            The distance map. Format: ``Im_Scalar``

        Returns
        -------
        v
            The depth map. Format: ``Im_Depth``
        """
        # based on https://github.com/apple/ml-hypersim/issues/9#issuecomment-754935697
        fltFocal = 886.81
        _, intHeight, intWidth = dist_map.shape

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

        depth_vals = (
            dist_map / np.linalg.norm(xyz_vals, ord=2, axis=0, keepdims=True) * fltFocal
        )
        return depth_vals

    def _read_distance_map(self, path: Path) -> np.ndarray:
        """
        Read a distance map from a hdf5 file.

        Returns
        -------
        v
            The distance map. Format: ``Im_Scalar``
        """
        f = io.BytesIO(self._file_loader(path))

        with self._file_type(f) as h_file:
            dataset = h_file["dataset"]
            dist_array = np.expand_dims(np.array(dataset).astype(np.float32), axis=0)

        return dist_array

    def _read_sdr_image(self, path: Path) -> np.ndarray:
        """
        Read an SDR image from a given file.

        Parameters
        ----------
        path
            The path of the image.

        Returns
        -------
        v
            The read image. Format: ``Im_RGB``
        """
        f = io.BytesIO(self._file_loader(path))
        im = self._image_type.open(f)
        im_arr = np.array(im).astype(np.float32) / 255
        im_arr = im_arr.transpose([2, 0, 1])
        return im_arr

    def __getitem__(self, index: SupportsIndex, /) -> "Sample":
        ai, cam, frame = self._split_data[index]

        depth_path = (
            self._hypersim_dir
            / ai
            / "images"
            / f"scene_{cam}_geometry_hdf5"
            / f"{frame}.depth_meters.hdf5"
        )

        if self.tonemap == "jpeg":
            sdr_path = (
                self._hypersim_dir
                / ai
                / "images"
                / f"scene_{cam}_final_preview"
                / f"{frame}.tonemap.jpg"
            )
            sdr_im = self._read_sdr_image(sdr_path)
        else:
            tonemap = cast(_TonemapFn, self.tonemap)
            sdr_im = tonemap(
                dataset_dir=self.hypersim_dir,
                ai=ai,
                cam=cam,
                frame=frame,
                file_loader=self._file_loader,
            )

        dist_map = self._read_distance_map(depth_path)
        depth_map = SimplifiedHypersimDataset._dist_2_depth(dist_map)

        mask = np.full(depth_map.shape, True)
        mask[np.isnan(depth_map)] = False

        depth_map[np.isnan(depth_map)] = 0

        cam_model = self._gl_cam_dict[ai]

        id = f"{ai},{cam},{frame}"

        return {
            "name": id,
            "rgb": sdr_im,
            "depth": depth_map,
            "camera": cam_model,
            "mask": mask,
        }

    def __iter__(self) -> Iterator[Sample]:
        for i in range(len(self)):
            yield self[i]


class _TonemapFn(Protocol):
    def __call__(
        self,
        dataset_dir: Path,
        ai: str,
        cam: str,
        frame: str,
        file_loader: Callable[[Path], bytes],
    ) -> np.ndarray: ...
