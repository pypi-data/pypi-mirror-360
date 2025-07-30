"""Unit tests for the image package."""

import pytest
import numpy as np

from mynd.image import (
    PixelFormat,
    ImageLayout,
    Image,
    ImageComposite,
    ImageType,
)


@pytest.fixture
def sample_image_data():
    return np.random.randint(0, 256, size=(100, 100, 3), dtype=np.uint8)


@pytest.fixture
def sample_image(sample_image_data):
    return Image.from_array(sample_image_data, PixelFormat.RGB)


def test_pixel_format():
    assert PixelFormat.GRAY.value == "gray"
    assert PixelFormat.RGB.value == "rgb"
    assert PixelFormat.RGBA.value == "rgba"


def test_image_layout():
    layout = ImageLayout(height=100, width=200, channels=3)
    assert layout.height == 100
    assert layout.width == 200
    assert layout.channels == 3
    assert layout.shape == (100, 200, 3)


def test_image_properties(sample_image):
    assert sample_image.pixel_format == PixelFormat.RGB
    assert sample_image.height == 100
    assert sample_image.width == 100
    assert sample_image.channels == 3
    assert sample_image.shape == (100, 100, 3)
    assert sample_image.dtype == np.uint8
    assert sample_image.ndim == 3


def test_image_from_array(sample_image_data):
    image = Image.from_array(sample_image_data, PixelFormat.RGB)
    assert isinstance(image, Image)
    assert image.pixel_format == PixelFormat.RGB
    assert image.shape == sample_image_data.shape


def test_image_to_array(sample_image, sample_image_data):
    array = sample_image.to_array()
    assert np.array_equal(array, sample_image_data)
    assert array is not sample_image._data  # Check if it's a copy


def test_image_copy(sample_image):
    copied_image = sample_image.copy()
    assert copied_image is not sample_image
    assert np.array_equal(copied_image.to_array(), sample_image.to_array())


def test_image_composite():
    image1 = Image.from_array(np.zeros((10, 10, 3)), PixelFormat.RGB)
    image2 = Image.from_array(np.ones((20, 20, 1)), PixelFormat.GRAY)

    composite = ImageComposite({ImageType.COLOR: image1, ImageType.RANGE: image2})

    assert ImageType.COLOR in composite
    assert ImageType.RANGE in composite
    assert ImageType.NORMAL not in composite

    assert composite.keys == [ImageType.COLOR, ImageType.RANGE]
    assert composite.get(ImageType.COLOR) == image1
    assert composite.get(ImageType.RANGE) == image2
    assert composite.get(ImageType.NORMAL) is None

    layouts = composite.get_layouts()
    assert layouts[ImageType.COLOR].shape == (10, 10, 3)
    assert layouts[ImageType.RANGE].shape == (20, 20, 1)

    pixel_formats = composite.get_pixel_formats()
    assert pixel_formats[ImageType.COLOR] == PixelFormat.RGB
    assert pixel_formats[ImageType.RANGE] == PixelFormat.GRAY


@pytest.mark.parametrize("pixel_format", list(PixelFormat))
def test_all_pixel_formats(pixel_format):
    data = np.random.randint(0, 256, size=(10, 10, 3), dtype=np.uint8)
    image = Image.from_array(data, pixel_format)
    assert image.pixel_format == pixel_format


def test_invalid_image_data():
    with pytest.raises(ValueError):
        Image.from_array(
            np.zeros((10, 10, 10, 10)), PixelFormat.RGB
        )  # 4D array for RGB
