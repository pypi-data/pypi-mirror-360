"""Module for camera helper functions."""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import TypeAlias

import Metashape as ms
import numpy as np
import polars as pl

from mynd.utils.literals import literal_primitive

from myndms.common.math import matrix_to_array, vector_to_array


def tabulate_camera_attributes(chunk: ms.Chunk) -> pl.DataFrame:
    """Returns a table of camera attributes from a chunk."""

    items: list[dict] = list()
    for camera in chunk.cameras:
        item: dict = {
            "camera_key": camera.key,
            "camera_label": camera.label,
            "image_label": Path(camera.photo.path).stem,
            "master_key": camera.master.key,
            "master_label": camera.master.label,
            "sensor_key": camera.sensor.key,
            "sensor_label": camera.sensor.label,
        }
        items.append(item)

    df: pl.DataFrame = pl.from_dicts(items)
    df: pl.DataFrame = _add_chunk_identifier_columns(df, chunk)

    return df


def tabulate_camera_images(chunk: ms.Chunk) -> pl.DataFrame:
    """Returns a table of camera image label from a chunk."""

    items: list[dict] = list()
    for camera in chunk.cameras:
        item: dict = {
            "camera_key": camera.key,
            "camera_label": camera.label,
            "image_label": Path(camera.photo.path).stem,
            "image_path": str(camera.photo.path),
        }
        items.append(item)

    df: pl.DataFrame = pl.from_dicts(items)
    df: pl.DataFrame = _add_chunk_identifier_columns(df, chunk)

    return df


MetadataValue: TypeAlias = str | bool | int | float
MetadataMap: TypeAlias = dict[str, MetadataValue]


def tabulate_camera_metadata(chunk: ms.Chunk) -> pl.DataFrame:
    """Returns a table of camera metadata from a chunk."""
    items: list[dict] = list()
    for camera in chunk.cameras:
        item: dict = {
            "camera_key": camera.key,
            "camera_label": camera.label,
        }
        item.update(get_camera_metadata(camera))
        items.append(item)
    df: pl.DataFrame = pl.from_dicts(items)
    df: pl.DataFrame = _add_chunk_identifier_columns(df, chunk)
    return df


def get_camera_metadata(camera: ms.Camera) -> dict:
    """Converts a camera and its metadata to a dictionary."""
    fields: dict[str, MetadataValue] = {
        key: literal_primitive(value) for key, value in camera.meta.items()
    }
    return fields


def tabulate_camera_sensors(chunk: ms.Chunk) -> pl.DataFrame:
    """Returns a table of camera sensors."""

    items: list[dict] = list()
    for sensor in chunk.sensors:
        item: dict = _convert_sensor_to_dict(sensor)
        items.append(item)

    df: pl.DataFrame = pl.from_dicts(items)
    df: pl.DataFrame = df.with_columns(
        [
            pl.col("location").cast(pl.Array(pl.Float64, shape=(3,))),
            pl.col("rotation").cast(pl.Array(pl.Float64, shape=(3, 3))),
        ]
    )

    df: pl.DataFrame = _add_chunk_identifier_columns(df, chunk)
    return df


def _add_chunk_identifier_columns(df: pl.DataFrame, chunk: ms.Chunk) -> pl.DataFrame:
    """Adds the chunk key and label as columns to the data frame."""
    df: pl.DataFrame = df.with_columns(
        [pl.lit(chunk.key).alias("chunk_key"), pl.lit(chunk.label).alias("chunk_label")]
    )
    return df


def _convert_sensor_to_dict(sensor: ms.Sensor) -> dict:
    """Converts a sensor to a dictionary."""

    item: dict = {
        "sensor_key": sensor.key,
        "sensor_label": sensor.label,
        "master_key": sensor.master.key,
        "master_label": sensor.master.label,
        "width": sensor.width,
        "height": sensor.height,
        "bands": sensor.bands,
        "layer_index": sensor.layer_index,
        "planes": [plane.key for plane in sensor.planes],
    }

    location: list[float] = _get_sensor_location_metric(sensor)
    rotation: list[list[float]] = _get_sensor_location_opencv(sensor)

    item["location"] = location
    item["rotation"] = rotation

    calibration: CalibrationOpenCV = convert_calibration_to_opencv(sensor.calibration)
    item.update(calibration.to_dict())

    return item


def _get_sensor_location_metric(sensor: ms.Sensor) -> list[float]:
    """Computes a sensors metric location."""
    location: np.ndarray = vector_to_array(
        sensor.location * sensor.chunk.transform.scale
    )
    return location.tolist()


def _get_sensor_location_opencv(sensor: ms.Sensor) -> list[list[float]]:
    """Computes a sensors rotation with OpenCV convention."""
    rotation: np.ndarray = matrix_to_array(sensor.rotation).T
    return rotation.tolist()


@dataclass(frozen=True)
class CalibrationOpenCV:
    """Class representing an OpenCV calibration."""

    width: int
    height: int

    fx: float
    fy: float

    cx: float
    cy: float

    k1: float
    k2: float
    k3: float

    p1: float
    p2: float

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the instance."""
        return {key: value for key, value in asdict(self).items()}


def convert_calibration_to_opencv(calibration: ms.Calibration) -> dict[str, float]:
    """Converts a calibration to OpenCV format and returns it as a dictionary."""
    half_width: int = calibration.width / 2
    half_height: int = calibration.height / 2

    fx: float = calibration.f + calibration.b1
    fy: float = calibration.f

    cx: float = calibration.cx + half_width - 0.5
    cy: float = calibration.cy + half_height - 0.5

    opencv_calibration: CalibrationOpenCV = CalibrationOpenCV(
        width=calibration.width,
        height=calibration.height,
        fx=fx,
        fy=fy,
        cx=cx,
        cy=cy,
        k1=calibration.k1,
        k2=calibration.k2,
        k3=calibration.k3,
        p1=calibration.p2,
        p2=calibration.p1,
    )

    return opencv_calibration
