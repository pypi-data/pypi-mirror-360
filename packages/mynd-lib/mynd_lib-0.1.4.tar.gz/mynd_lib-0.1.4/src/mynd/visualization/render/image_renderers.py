"""Module for image visualization functionality."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import NamedTuple, Optional

import cv2
import numpy as np

from mynd.image import Image, PixelFormat
from mynd.image import convert_image_to_rgb, normalize_image, apply_color_map

from mynd.geometry.stereo import StereoGeometry
from mynd.geometry.stereo import PixelMap, remap_image_pixels

from mynd.utils.containers import Pair
from mynd.utils.key_codes import KeyCode


class WindowHandle(NamedTuple):
    """Class representing a window handle."""

    name: str
    width: int
    height: int


class TrackbarData(NamedTuple):
    """Class representing trackbar data."""

    name: str
    lower: int | float
    upper: int | float
    callback: Callable[[int | float], None]


def create_window(
    window_name: str = "Window",
    width: int = 800,
    height: int = 1200,
    track_bars: Optional[list[TrackbarData]] = None,
) -> WindowHandle:
    """Creates a window with optional track bars."""

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, width, height)

    if track_bars:
        for track_bar in track_bars:
            cv2.createTrackbar(
                track_bar.name,
                window_name,
                track_bar.lower,
                track_bar.upper,
                track_bar.callback,
            )

    return WindowHandle(name=window_name, width=width, height=height)


def destroy_window(window: WindowHandle) -> None:
    """Destroys a window."""
    cv2.destroyWindow(window.name)


def destroy_all_windows() -> None:
    """Destroys all the windows."""
    cv2.destroyAllWindows()


def render_image(window: WindowHandle, image: Image | np.ndarray) -> None:
    """Renders an array of values into an image."""
    if isinstance(image, Image):
        values: np.ndarray = image.to_array()
    else:
        values: np.ndarray = image

    cv2.imshow(window.name, values)


def wait_key_input(wait: int) -> KeyCode:
    """Waits for a keyboard input."""
    key: int = cv2.waitKey()
    try:
        key_code: KeyCode = KeyCode(key)
    except ValueError:
        key_code: KeyCode = KeyCode.NULL
    return key_code


@dataclass
class StereoWindows:
    """Class representing a collection of windows for rendering stereo data."""

    color_left: WindowHandle
    color_right: WindowHandle

    range_left: WindowHandle
    range_right: WindowHandle


def create_stereo_windows() -> StereoWindows:
    """Creates a collection of windows for rendering stereo geometries."""
    return StereoWindows(
        color_left=create_window("color_left", 680, 512),
        color_right=create_window("color_right", 680, 512),
        range_left=create_window("range_left", 680, 512),
        range_right=create_window("range_right", 680, 512),
    )


def distort_range_maps(ranges: Pair[Image], pixel_maps: Pair[PixelMap]) -> Pair[Image]:
    """Distorts a pair of range maps."""

    first: Image = remap_image_pixels(image=ranges.first, pixel_map=pixel_maps.first)
    second: Image = remap_image_pixels(image=ranges.second, pixel_map=pixel_maps.second)

    return Pair(first, second)


def render_stereo_geometry(
    windows: StereoWindows,
    geometry: StereoGeometry,
    distort: bool,
) -> None:
    """Render a stereo geometry into a collection of windows."""

    rectification = geometry.rectification

    normalized_ranges: Pair[Image] = Pair(
        first=normalize_image(
            geometry.range_maps.first, lower=0.0, upper=8.0, flip=True
        ),
        second=normalize_image(
            geometry.range_maps.second, lower=0.0, upper=8.0, flip=True
        ),
    )

    colored_ranges: Pair[Image] = Pair(
        first=apply_color_map(normalized_ranges.first),
        second=apply_color_map(normalized_ranges.second),
    )

    images: Pair[Image] = geometry.rectified_images

    if distort:
        images: Pair[Image] = geometry.raw_images
        colored_ranges: Pair[Image] = distort_range_maps(
            colored_ranges, rectification.inverse_pixel_maps
        )

    # Render images
    render_image(windows.color_left, images.first)
    render_image(windows.color_right, images.second)

    # Render range maps
    render_image(windows.range_left, colored_ranges.first)
    render_image(windows.range_right, colored_ranges.second)


def create_stereo_geometry_color_image(
    colors: Pair[Image],
    ranges: Pair[Image],
) -> Image:
    """Creates image tiles for a stereo geometry. Useful for visualizing the
    geometry as RGB."""

    colors: Pair[Image] = Pair(
        convert_image_to_rgb(colors.first),
        convert_image_to_rgb(colors.second),
    )

    normalized_ranges: Pair[Image] = Pair(
        first=normalize_image(ranges.first, lower=0.0, upper=8.0, flip=True),
        second=normalize_image(ranges.second, lower=0.0, upper=8.0, flip=True),
    )

    colored_ranges: Pair[Image] = Pair(
        first=apply_color_map(normalized_ranges.first),
        second=apply_color_map(normalized_ranges.second),
    )

    stacked_colors: np.ndarray = np.hstack(
        (colors.first.to_array(), colors.second.to_array())
    )
    stacked_ranges: np.ndarray = np.hstack(
        (colored_ranges.first.to_array(), colored_ranges.second.to_array())
    )

    combined_stacks: np.ndarray = np.vstack((stacked_colors, stacked_ranges))

    return Image.from_array(combined_stacks, pixel_format=PixelFormat.RGB)
