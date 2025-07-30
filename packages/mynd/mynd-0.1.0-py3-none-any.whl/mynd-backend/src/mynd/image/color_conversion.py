"""Module for common image processors."""

from typing import Literal

import cv2
import numpy as np

from .image_types import Image, PixelFormat


# Create a literal type to enable type annotations
ColorConversionCode = Literal[
    cv2.COLOR_GRAY2RGB,
    cv2.COLOR_GRAY2BGR,
    cv2.COLOR_GRAY2RGBA,
    cv2.COLOR_GRAY2BGRA,
    # GRAY -> RGB / BGR / RGBA / BGRA
    cv2.COLOR_RGB2GRAY,
    cv2.COLOR_RGB2BGR,
    cv2.COLOR_RGB2RGBA,
    cv2.COLOR_RGB2BGRA,
    # RGB -> GRAY / BGR / RGBA / BGRA
    cv2.COLOR_BGR2GRAY,
    cv2.COLOR_BGR2RGB,
    cv2.COLOR_BGR2RGBA,
    cv2.COLOR_BGR2BGRA,
    # BGR -> GRAY / RGB / RGBA / BGRA
    cv2.COLOR_RGBA2GRAY,
    cv2.COLOR_RGBA2RGB,
    cv2.COLOR_RGBA2BGR,
    cv2.COLOR_RGBA2BGRA,
    # RGBA -> GRAY / RGB / BGR / RGBA
    cv2.COLOR_BGRA2GRAY,
    cv2.COLOR_BGRA2RGB,
    cv2.COLOR_BGRA2BGR,
    cv2.COLOR_BGRA2RGBA,
]


def convert_image_color(image: Image, to_format: PixelFormat) -> Image:
    """Converts an image to the desired format."""
    from_format: PixelFormat = image.pixel_format
    conversion: ColorConversionCode = _map_formats_to_conversion(from_format, to_format)
    converted: np.ndarray = cv2.cvtColor(image.to_array(), conversion)
    return Image.from_array(converted, to_format)


def _map_formats_to_conversion(
    from_format: PixelFormat, to_format: PixelFormat
) -> ColorConversionCode:
    """Maps source and target pixel formats to a color convertsion function."""
    match from_format:
        case PixelFormat.GRAY:
            return _get_color_conversion_gray(to_format)
        case PixelFormat.RGB:
            return _get_color_conversion_rgb(to_format)
        case PixelFormat.BGR:
            return _get_color_conversion_bgr(to_format)
        case PixelFormat.RGBA:
            return _get_color_conversion_rgba(to_format)
        case PixelFormat.BGRA:
            return _get_color_conversion_bgra(to_format)
        case _:
            raise NotImplementedError(f"invalid pixel format: {from_format}")


def _get_color_conversion_gray(to_format: PixelFormat) -> ColorConversionCode:
    """Gets the color conversion format for grayscale images."""
    match to_format:
        case PixelFormat.RGB:
            return cv2.COLOR_GRAY2RGB
        case PixelFormat.BGR:
            return cv2.COLOR_GRAY2BGR
        case PixelFormat.RGBA:
            return cv2.COLOR_GRAY2RGBA
        case PixelFormat.BGRA:
            return cv2.COLOR_GRAY2BGRA
        case _:
            raise NotImplementedError(f"invalid target format: {to_format}")


def _get_color_conversion_rgb(to_format: PixelFormat) -> ColorConversionCode:
    """Gets the color conversion format for RGB images."""
    match to_format:
        case PixelFormat.GRAY:
            return cv2.COLOR_RGB2GRAY
        case PixelFormat.BGR:
            return cv2.COLOR_RGB2BGR
        case PixelFormat.RGBA:
            return cv2.COLOR_RGB2RGBA
        case PixelFormat.BGRA:
            return cv2.COLOR_RGB2BGRA
        case _:
            raise NotImplementedError(f"invalid target format: {to_format}")


def _get_color_conversion_bgr(to_format: PixelFormat) -> ColorConversionCode:
    """Gets the color conversion format for BGR images."""
    match to_format:
        case PixelFormat.GRAY:
            return cv2.COLOR_BGR2GRAY
        case PixelFormat.RGB:
            return cv2.COLOR_BGR2RGB
        case PixelFormat.RGBA:
            return cv2.COLOR_BGR2RGBA
        case PixelFormat.BGRA:
            return cv2.COLOR_BGR2BGRA
        case _:
            raise NotImplementedError(f"invalid target format: {to_format}")


def _get_color_conversion_rgba(to_format: PixelFormat) -> ColorConversionCode:
    """Gets the color conversion format for RGBA images."""
    match to_format:
        case PixelFormat.GRAY:
            return cv2.COLOR_RGBA2GRAY
        case PixelFormat.RGB:
            return cv2.COLOR_RGBA2RGB
        case PixelFormat.BGR:
            return cv2.COLOR_RGBA2BGR
        case PixelFormat.BGRA:
            return cv2.COLOR_RGBA2BGRA
        case _:
            raise NotImplementedError(f"invalid color format: {to_format}")


def _get_color_conversion_bgra(to_format: PixelFormat) -> ColorConversionCode:
    """Gets the color conversion format for BGRA images."""
    match to_format:
        case PixelFormat.GRAY:
            return cv2.COLOR_BGRA2GRAY
        case PixelFormat.RGB:
            return cv2.COLOR_BGRA2RGB
        case PixelFormat.BGR:
            return cv2.COLOR_BGRA2BGR
        case PixelFormat.RGBA:
            return cv2.COLOR_BGRA2RGBA
        case _:
            raise NotImplementedError(f"invalid color format: {to_format}")


def convert_image_to_rgb(image: Image) -> Image:
    """Converts an image to RGB."""
    match image.pixel_format:
        case PixelFormat.GRAY:
            return _convert_grayscale_to_rgb(image)
        case PixelFormat.RGB:
            return image
        case _:
            raise NotImplementedError("invalid image pixel format")


def _convert_grayscale_to_rgb(image: Image) -> Image:
    """Converts a grayscale image to RGB."""
    values: np.ndarray = cv2.cvtColor(image.to_array(), cv2.COLOR_GRAY2RGB)
    return Image.from_array(values, PixelFormat.RGB)


def apply_color_map(image: Image) -> Image:
    """Applies a color map to the image values."""
    values: np.ndarray = cv2.applyColorMap(image.to_array(), cv2.COLORMAP_JET)
    return Image.from_array(values, PixelFormat.RGB)
