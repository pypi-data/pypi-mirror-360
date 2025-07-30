"""Module for image functionality for the Metashape backend."""

import Metashape as ms
import numpy as np

from mynd.image import Image, PixelFormat


def convert_image(image: ms.Image) -> Image:
    """Converts a Metashape image to an internal image."""

    pixel_format: PixelFormat = _get_format_from_image(image)
    data: np.ndarray = _image_buffer_to_array(image)

    return Image.from_array(data=data, pixel_format=pixel_format)


def _image_dtype_to_numpy(image: ms.Image) -> np.dtype:
    """Converts a Metashape image data type to a Numpy dtype."""

    match image.data_type:
        case "U8":
            return np.uint8
        case "U16":
            return np.uint16
        case "U32":
            return np.uint32
        case "U64":
            return np.uint64
        case "F16":
            return np.float16
        case "F32":
            return np.float32
        case "F64":
            return np.float64
        case _:
            raise NotImplementedError("unknown data type in convert_data_type_to_numpy")


def _get_format_from_image(image: ms.Image) -> PixelFormat:
    """Returns an image format based on the image channels."""

    channels: str = image.channels.lower()

    match channels:
        case "gray" | "i":
            return PixelFormat.GRAY
        case "x":
            return PixelFormat.X
        case "rgb":
            return PixelFormat.RGB
        case "bgr":
            return PixelFormat.BGR
        case "xyz":
            return PixelFormat.XYZ
        case "rgba":
            return PixelFormat.RGBA
        case "bgra":
            return PixelFormat.BGRA
        case _:
            return PixelFormat.UNKNOWN


def _image_buffer_to_array(image: ms.Image) -> np.ndarray:
    """Converts a Metashape image to a Numpy array."""

    data_type: np.dtype = _image_dtype_to_numpy(image)

    image_array = np.frombuffer(image.tostring(), dtype=data_type)
    assert len(image_array) == image.height * image.width * image.cn
    image_array: np.ndarray = image_array.reshape(image.height, image.width, image.cn)

    return image_array
