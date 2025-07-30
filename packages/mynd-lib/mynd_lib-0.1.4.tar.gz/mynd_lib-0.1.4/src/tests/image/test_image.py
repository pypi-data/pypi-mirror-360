"""Unit tests for the image package."""

import pytest
import numpy as np

from mynd.image import Image


@pytest.fixture
def sample_image_data():
    return np.random.randint(0, 256, size=(100, 100, 3), dtype=np.uint8)


@pytest.fixture
def sample_image(sample_image_data):
    return Image.from_array(sample_image_data, Image.Format.RGB)


def test_pixel_format():
    assert Image.Format.GRAY.value == "gray"
    assert Image.Format.RGB.value == "rgb"
    assert Image.Format.RGBA.value == "rgba"


def test_image_layout():
    layout = Image.Layout(height=100, width=200, channels=3)
    assert layout.height == 100
    assert layout.width == 200
    assert layout.channels == 3
    assert layout.shape == (100, 200, 3)


def test_image_properties(sample_image):
    assert sample_image.pixel_format == Image.Format.RGB
    assert sample_image.height == 100
    assert sample_image.width == 100
    assert sample_image.channels == 3
    assert sample_image.shape == (100, 100, 3)
    assert sample_image.dtype == np.uint8
    assert sample_image.ndim == 3


def test_image_from_array(sample_image_data):
    image = Image.from_array(sample_image_data, Image.Format.RGB)
    assert isinstance(image, Image)
    assert image.pixel_format == Image.Format.RGB
    assert image.shape == sample_image_data.shape


def test_image_to_array(sample_image, sample_image_data):
    array = sample_image.to_array()
    assert np.array_equal(array, sample_image_data)
    assert array is not sample_image._data  # Check if it's a copy


def test_image_copy(sample_image):
    copied_image = sample_image.copy()
    assert copied_image is not sample_image
    assert np.array_equal(copied_image.to_array(), sample_image.to_array())


@pytest.mark.parametrize("pixel_format", list(Image.Format))
def test_all_pixel_formats(pixel_format):
    data = np.random.randint(0, 256, size=(10, 10, 3), dtype=np.uint8)
    image = Image.from_array(data, pixel_format)
    assert image.pixel_format == pixel_format


def test_invalid_image_data():
    with pytest.raises(ValueError):
        Image.from_array(
            np.zeros((10, 10, 10, 10)), Image.Format.RGB
        )  # 4D array for RGB
