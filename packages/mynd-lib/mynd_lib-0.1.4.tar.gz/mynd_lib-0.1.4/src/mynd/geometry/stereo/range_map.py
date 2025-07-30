"""Module for functionality related to range maps. Currently the module includes functionality
for computing range from disparity, 3D points from range, and normal maps from range maps."""

import warnings

import kornia
import kornia.geometry.depth as kgd
import numpy as np
import torch

from mynd.image import Image, PixelFormat


warnings.warn = lambda *args, **kwargs: None


def compute_ranges_from_disparities(
    disparity: Image,
    baseline: float,
    focal_length: float,
) -> Image:
    """Computes a range map from the given disparity map and camera matrix. Returns the
    range map as a HxW array with float32 values."""

    assert (
        disparity.pixel_format == PixelFormat.X
    ), f"invalid disparity map format: {disparity.pixel_format}"

    # Kornia expects a disparity tensor of shape Bx1xHxW
    range_tensor: torch.Tensor = kgd.depth_from_disparity(
        disparity=_disparity_map_to_tensor(disparity.to_array()),
        baseline=baseline,
        focal=focal_length,
    )

    range_values: np.ndarray = _range_tensor_to_numpy(range_tensor)

    return Image.from_array(range_values, PixelFormat.X)


def compute_points_from_ranges(
    range_map: Image,
    camera_matrix: np.ndarray,
    normalize_points: bool = False,
) -> Image:
    """Computes 3D points based on the given range map and camera matrix. Returns
    the points as a HxWx3 array with float32 values."""

    assert (
        range_map.pixel_format == PixelFormat.X
    ), f"invalid range map format: {range_map.pixel_format}"

    # Kornia expects a range tensor of shape Bx1xHxW
    points_tensor: torch.Tensor = kgd.depth_to_3d_v2(
        depth=_range_map_to_tensor(range_map.to_array()),
        camera_matrix=_camera_matrix_to_tensor(camera_matrix),
        normalize_points=normalize_points,
    )

    # Convert 3D points back to XYZ format
    point_values: np.ndarray = _point_tensor_to_numpy(points_tensor)

    return Image.from_array(point_values, PixelFormat.XYZ)


def compute_normals_from_ranges(
    range_map: Image,
    camera_matrix: np.ndarray,
    flipped: bool = False,
    normalize_points: bool = False,
) -> Image:
    """Computes normal map based on the given range map and camera matrix. Returns
    the normals as float32 unit vectors. If flipped is true, the normals are defined
    with positive x-, y-, and z pointing right, down, and away as seen by the camera.
    """

    assert (
        range_map.pixel_format == PixelFormat.X
    ), f"invalid range map format: {range_map.pixel_format}"

    normal_tensor: torch.Tensor = kgd.depth_to_normals(
        depth=_range_map_to_tensor(range_map.to_array()),
        camera_matrix=_camera_matrix_to_tensor(camera_matrix),
        normalize_points=normalize_points,
    )

    normals: np.ndarray = _normal_tensor_to_numpy(normal_tensor)
    normals: np.ndarray = _normalize_normal_map(normals)

    if flipped:
        normals: np.ndarray = -normals

    # TODO: Convert to int8
    normals: np.ndarray = _convert_normal_map_to_int8(normals)

    return Image.from_array(normals, PixelFormat.XYZ)


def fill_range_map_dilation(range_map: Image) -> Image:
    """Fills a range map by dilation."""

    assert isinstance(range_map, Image), "invalid range map type"

    range_values: np.ndarray = np.squeeze(range_map.to_array())

    RANGE_LOWER: float = 0.1
    mask: np.ndarray = range_values < RANGE_LOWER
    KERNEL: torch.Tensor = torch.ones(51, 51)

    # TODO: Downscale range maps to increase computational efficiency
    range_tensor: torch.Tensor = _range_map_to_tensor(range_values)
    dilated_range_tensor: torch.Tensor = kornia.morphology.dilation(
        range_tensor, KERNEL, engine="unfold"
    )
    dilated_range_array: np.ndarray = _range_tensor_to_numpy(dilated_range_tensor)

    range_values[mask] = dilated_range_array[mask]

    return Image.from_array(range_values, pixel_format=range_map.pixel_format)


def _camera_matrix_to_tensor(camera_matrix: np.ndarray) -> torch.Tensor:
    """Converts a 3x3 camera matrix into a 1x3x3 torch tensor."""
    assert camera_matrix.shape == (
        3,
        3,
    ), f"invalid camera matrix shape: {camera_matrix.shape}"
    camera_matrix: np.ndarray = np.squeeze(camera_matrix)
    return torch.from_numpy(camera_matrix.copy()).view(1, 3, 3)


def _normalize_normal_map(normals: np.ndarray) -> np.ndarray:
    """Normalizes normals by their L2 norm."""
    norms: np.ndarray = np.linalg.norm(normals, axis=2)

    NORM_THRESHOLD: float = 0.0000001
    invalid: np.ndarray = norms < NORM_THRESHOLD
    norms[invalid] = 1.0
    normals[invalid] = np.zeros(3)

    # Convert normals into unit vectors
    normals /= norms[:, :, np.newaxis]
    return normals


def _convert_normal_map_to_int8(normals: np.ndarray) -> np.ndarray:
    """Converts a normal map from float32 unit vectors to int8 data type."""
    scale: int = np.iinfo(np.int8).max
    return np.round(scale * normals).astype(np.int8)


def _range_map_to_tensor(range_map: np.ndarray) -> torch.Tensor:
    """Converts a HxWx1 range map into a 1x1xHxW torch tensor."""
    range_map: np.ndarray = np.squeeze(range_map)
    return torch.from_numpy(range_map.copy()).view(
        1, 1, range_map.shape[0], range_map.shape[1]
    )


def _disparity_map_to_tensor(disparity: np.ndarray) -> torch.Tensor:
    """Converts a HxW disparity map into a 1x1xHxW torch tensor."""
    disparity: np.ndarray = np.squeeze(disparity)
    return torch.from_numpy(disparity.copy()).view(
        1, 1, disparity.shape[0], disparity.shape[1]
    )


def _range_map_to_tensor(range_map: np.ndarray) -> torch.Tensor:
    """Converts a HxW range map into a 1x1xHxW torch tensor."""
    range_map: np.ndarray = np.squeeze(range_map)
    return torch.from_numpy(range_map.copy()).view(
        1, 1, range_map.shape[0], range_map.shape[1]
    )


def _range_tensor_to_numpy(range_tensor: torch.Tensor) -> np.ndarray:
    """Converts a 1x1xHxW range map into a HxWx1 array."""
    assert (
        range_tensor.shape[0] == 1
    ), f"invalid range tensor shape - {range_tensor.shape}"
    assert (
        range_tensor.shape[1] == 1
    ), f"invalid range tensor shape - {range_tensor.shape}"
    return np.squeeze(range_tensor.numpy()).astype(np.float32)


def _point_tensor_to_numpy(point_tensor: torch.Tensor) -> np.ndarray:
    """Converts a 1x3xHxW point tensor into a HxWx3 array"""
    assert (
        point_tensor.shape[0] == 1
    ), f"invalid point tensor shape - {point_tensor.shape}"
    assert (
        point_tensor.shape[1] == 3
    ), f"invalid point tensor shape - {point_tensor.shape}"
    return np.squeeze(point_tensor.numpy()).transpose((1, 2, 0)).astype(np.float32)


def _normal_tensor_to_numpy(normal_tensor: torch.Tensor) -> np.ndarray:
    """Converts a 1x3xHxW points tensor into a HxWx3 array"""
    assert (
        normal_tensor.shape[0] == 1
    ), f"invalid points tensor shape - {normal_tensor.shape}"
    assert (
        normal_tensor.shape[1] == 3
    ), f"invalid points tensor shape - {normal_tensor.shape}"
    return np.squeeze(normal_tensor.numpy()).transpose((1, 2, 0)).astype(np.float32)
