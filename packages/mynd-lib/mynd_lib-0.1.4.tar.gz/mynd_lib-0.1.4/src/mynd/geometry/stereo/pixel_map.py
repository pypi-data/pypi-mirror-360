"""Module for geometric image transformations."""

from dataclasses import dataclass
from typing import Self

import cv2
import numpy as np

from mynd.image import Image


@dataclass(frozen=True)
class PixelMap:
    """Class representing a pixel map. The pixel map data is an
    array of size HxWx2 with the X and Y pixel maps respectively."""

    data: np.ndarray

    def __post_init__(self: Self) -> None:
        """Validates the pixel map."""
        assert self.data.dtype in [np.float32, float], "invalid pixel map dtype"
        assert self.data.ndim == 3, "invalid pixel map dimensions"
        assert self.data.shape[2] == 2, "invalid pixel map shape"

    @property
    def height(self: Self) -> int:
        """Returns the height of the pixel map."""
        return self.data.shape[0]

    @property
    def width(self: Self) -> int:
        """Returns the width of the pixel map."""
        return self.data.shape[1]

    @property
    def shape(self: Self) -> tuple[int, int, int]:
        """Returns the shape of the pixel map."""
        return self.data.shape

    @property
    def ndim(self: Self) -> int:
        """Returns the dimension count of the pixel map."""
        return self.data.ndim

    @property
    def dtype(self: Self) -> type:
        """Returns the data type of the pixel map."""
        return self.data.dtype

    @property
    def x(self: Self) -> np.ndarray:
        """Returns the x component of the pixel map."""
        return self.data[:, :, 0]

    @property
    def y(self: Self) -> np.ndarray:
        """Returns the y component of the pixel map."""
        return self.data[:, :, 1]

    def to_array(self: Self) -> np.ndarray:
        """Returns the pixel map as an array."""
        return self.data.copy()


def compute_pixel_map(
    camera_matrix: np.ndarray,
    distortion: np.ndarray,
    rotation: np.ndarray,
    new_camera_matrix: np.ndarray,
    desired_resolution: tuple[int, int],
) -> PixelMap:
    """Computes a pixel map that maps the image as seen by original camera matrix,
    to an image seen by the new camera matrix."""

    map_components: tuple[np.ndarray, np.ndarray] = cv2.initUndistortRectifyMap(
        camera_matrix,
        distortion,
        rotation,
        new_camera_matrix,
        desired_resolution,
        cv2.CV_32FC1,
    )

    return PixelMap(np.stack((map_components[0], map_components[1]), axis=-1))


def invert_pixel_map(
    pixel_map: PixelMap,
    *,
    iterations: int = 20,
    step_size: float = 0.5,
) -> PixelMap:
    """Computes the inverse of a pixel map using iteration. The function
    takes a HxWx2 array representing a map from indices to subpixel index,
    and returns a HxWx2 array representing the inverse map."""

    height: int = pixel_map.height
    width: int = pixel_map.width

    identity = np.zeros_like(pixel_map.data)
    identity[:, :, 1], identity[:, :, 0] = np.indices((height, width))  # identity map
    inverse_map_data: np.ndarray = np.copy(identity)

    for index in range(iterations):
        correction: np.ndarray = identity - cv2.remap(
            src=pixel_map.data,
            map1=inverse_map_data,
            map2=None,
            borderMode=cv2.BORDER_DEFAULT,
            interpolation=cv2.INTER_LINEAR,
        )
        inverse_map_data += correction * step_size

    return PixelMap(inverse_map_data)


def remap_image_pixels(
    image: Image,
    pixel_map: PixelMap,
    *,
    border_value: int | float = 0,
    border_mode: int = cv2.BORDER_CONSTANT,
    interpolation: int = cv2.INTER_LINEAR,
) -> Image:
    """Applies a pixel map to the pixels of the image."""
    mapped: np.ndarray = cv2.remap(
        src=image.to_array(),
        map1=pixel_map.to_array(),
        map2=None,
        borderValue=border_value,
        borderMode=border_mode,
        interpolation=interpolation,
    )

    if mapped.ndim == 2:
        mapped: np.ndarray = np.expand_dims(mapped, axis=2)

    return Image.from_array(data=mapped, pixel_format=image.pixel_format)
