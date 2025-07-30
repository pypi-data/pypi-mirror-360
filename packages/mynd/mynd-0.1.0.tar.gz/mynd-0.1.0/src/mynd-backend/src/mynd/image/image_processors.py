"""Module for common image processors."""

import cv2
import numpy as np

from .image_types import Image, PixelFormat


def flip_image(image: Image, axis: int = 1) -> Image:
    """Flip an image around the specified axis."""
    flipped_values: np.ndarray = cv2.flip(image.to_array(), axis)
    flipped: Image = Image.from_array(
        data=flipped_values,
        pixel_format=image.pixel_format,
    )
    return flipped


def resize_image(image: Image, height: int, width: int) -> Image:
    """Resize an image to the desired size. The size is specified as HxW"""
    return Image.from_array(
        data=cv2.resize(image.to_array(), (width, height), cv2.INTER_AREA),
        pixel_format=image.pixel_format,
    )


def process_image_clahe(image: Image, size: int, clip: float) -> Image:
    """Filter an image with CLAHE."""
    # NOTE: This function only works on uint8 images for now
    assert image.dtype == np.uint8, f"invalid image dtype: {image.dtype}"

    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(size, size))

    match image.pixel_format:
        case PixelFormat.GRAY:
            return _process_image_clahe_gray(image, clahe)
        case PixelFormat.RGB | PixelFormat.BGR:
            return _process_image_clahe_rgb(image, clahe)
        case _:
            raise NotImplementedError(f"invalid pixel format: {image.pixel_format}")

    raise NotImplementedError


def _process_image_clahe_rgb(image: Image, processor: object) -> Image:
    """Applies CLAHE to a RGB / BGR image via LAB color space."""

    match image.pixel_format:
        case PixelFormat.RGB:
            format_to = cv2.COLOR_RGB2LAB
            format_from = cv2.COLOR_LAB2RGB
        case PixelFormat.BGR:
            format_to = cv2.COLOR_BGR2LAB
            format_from = cv2.COLOR_LAB2BGR
        case _:
            raise NotImplementedError

    values: np.ndarray = cv2.cvtColor(image.to_array(), format_to)
    values[:, :, 0]: np.ndarray = processor.apply(values[:, :, 0])
    values: np.ndarray = cv2.cvtColor(values, format_from)

    return Image.from_array(values, image.pixel_format)


def _process_image_clahe_gray(image: Image, processor: object) -> Image:
    """Applies CLAHE to a grayscale image."""
    values: np.ndarray = image.to_array()
    values: np.ndarray = processor.apply(values)
    return Image.from_array(values, image.pixel_format)


def process_image_gamma(image: Image, gamma: float) -> Image:
    """Corrects the colors of an image with gamma correction."""
    values: np.ndarray = image.to_array()
    min_value: int | float = np.iinfo(image.dtype).min
    max_value: int | float = np.iinfo(image.dtype).max

    scale: int | float = max_value - min_value
    difference: np.ndarray = values - min_value

    corrected_values: np.ndarray = np.array(
        scale * (difference / scale) ** gamma, dtype=image.dtype
    )

    return Image.from_array(corrected_values, pixel_format=image.pixel_format)


def process_image_linear(image: Image, brightness: float, contrast: float) -> Image:
    """Corrects an image by apply a linear scale to the image brightness and contrast.
    :arg brightness:    scale value for the image brightness
    :arg contrast:      scale value for the image contrast
    """
    values: np.ndarray = image.to_array()

    min_value: int | float = np.iinfo(image.dtype).min
    max_value: int | float = np.iinfo(image.dtype).max
    scale: int | float = max_value - min_value

    normalized_values: np.ndarray = np.array(
        ((values - min_value) * brightness) / scale * contrast + 0.5 * (1 - contrast),
        dtype=np.float32,
    )

    # Clamp values that are outside the interval
    normalized_values[normalized_values > 1.0] = 1.0
    normalized_values[normalized_values < 0] = 0.0

    # Rescale values back to the range of the image
    corrected_values: np.ndarray = np.array(
        scale * normalized_values + min_value,
        dtype=image.dtype,
    )

    return Image.from_array(corrected_values, image.pixel_format)


def normalize_image(
    image: Image,
    lower: int | float | None = None,
    upper: int | float | None = None,
    flip: bool = False,
) -> Image:
    """Normalizes the values of an image to be between the lower and upper values."""
    values: np.ndarray = image.to_array()

    if lower:
        values[values < lower] = lower
    if upper:
        values[values > upper] = upper

    min_value: int | float = values.min()
    max_value: int | float = values.max()

    # TODO: Add support for multiple dtypes here
    if flip:
        scale: int = -255
        offset: int = 255
    else:
        scale: int = 255
        offset: int = 0

    # Normalized values between 0 and 1
    normalized: np.ndarray = (values - min_value) / (max_value - min_value)
    normalized: np.ndarray = scale * normalized + offset

    normalized: np.ndarray = normalized.astype(np.uint8)
    return Image.from_array(normalized, image.pixel_format)
