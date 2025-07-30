"""Module for IO functionality for images."""

from pathlib import Path

import imageio.v3 as iio
import numpy as np

from .image_types import Image, PixelFormat


def _infer_pixel_format(values: np.ndarray) -> PixelFormat:
    """Infers the image format based on the image data type and channel count."""

    dtype: np.dtype = values.dtype
    channels: int = values.shape[2]

    is_floating_point: bool = dtype in [np.float16, np.float32, np.float64]

    match channels:
        case 1:
            return PixelFormat.X if is_floating_point else PixelFormat.GRAY
        case 3:
            return PixelFormat.XYZ if is_floating_point else PixelFormat.RGB
        case 4:
            return PixelFormat.XYZW if is_floating_point else PixelFormat.RGBA
        case _:
            raise ValueError(
                f"invalid combination of dtype and channels: {dtype}, {values}"
            )


def read_image(
    uri: str | Path,
    *,
    index: int | None = None,
    plugin: str | None = None,
    extension: str | None = None,
    **kwargs,
) -> Image | str:
    """Reads an image from a uniform resource identifier (URI). The image format must
    either be GRAY, X, RGB, XYZ, RGBA, or XYZW. Returns an image with dimensions HxWxC.
    """
    try:
        values: np.ndarray = iio.imread(
            uri, index=index, plugin=plugin, extension=extension, **kwargs
        )

        if values.ndim != 3:
            values: np.ndarray = np.expand_dims(values, axis=2)

        _metadata: dict = iio.immeta(uri)
        pixel_format: PixelFormat = _infer_pixel_format(values)
        return Image.from_array(data=values, pixel_format=pixel_format)
    except (OSError, IOError, TypeError, ValueError) as error:
        return str(error)


def write_image(
    image: Image | np.ndarray,
    uri: str | Path,
    *,
    plugin: str | None = None,
    extension: str | None = None,
    **kwargs,
) -> Path | str:
    """Writes an image to a uniform resource identifier (URI). The image format
    must either be GRAY, RGB, or RGBA."""

    if isinstance(image, Image):
        values: np.ndarray = image.to_array()
    elif isinstance(image, np.ndarray):
        values: np.ndarray = image
    else:
        return f"invalid image type: {type(image)}"

    try:
        iio.imwrite(
            uri,
            np.squeeze(values),
            plugin=None,
            extension=None,
            format_hint=None,
            **kwargs,
        )
        return uri
    except (OSError, IOError, TypeError, ValueError) as error:
        return str(error)
