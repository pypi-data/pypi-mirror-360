"""Module for stereo helper functions."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar, TypeAlias

import Metashape as ms

from mynd.utils.containers import Pair
from mynd.utils.log import logger


@dataclass(frozen=True)
class StereoGroup:
    """Class representing a pair of stereo sensors and their corresponding camera pairs."""

    SensorPair: ClassVar[TypeAlias] = Pair[ms.Sensor]
    CameraPair: ClassVar[TypeAlias] = Pair[ms.Camera]

    sensor_pair: SensorPair
    camera_pairs: list[CameraPair]


def get_stereo_groups(chunk: ms.Chunk) -> list[StereoGroup]:
    """Composes stereo collections for the sensors and cameras in the chunk.
    Stereo collections are based on master-slave pairs of sensor and their
    corresponding cameras."""

    sensor_pairs: set[StereoGroup.SensorPair] = _get_sensor_pairs(chunk)
    camera_pairs: set[StereoGroup.CameraPair] = _get_camera_pairs(chunk)

    stereo_frames: list[StereoGroup] = [
        _group_stereo_data(sensor_pair, camera_pairs) for sensor_pair in sensor_pairs
    ]

    return stereo_frames


def _get_sensor_pairs(chunk: ms.Chunk) -> set[StereoGroup.SensorPair]:
    """Gets master-slave pairs of sensors from a ms chunk."""
    stereo_sensors: set[StereoGroup.SensorPair] = set(
        [
            StereoGroup.SensorPair(sensor.master, sensor)
            for sensor in chunk.sensors
            if sensor.master != sensor
        ]
    )
    return stereo_sensors


def _get_camera_pairs(chunk: ms.Chunk) -> set[StereoGroup.CameraPair]:
    """Gets master-slave pairs of cameras from a ms chunk."""
    stereo_cameras: set[StereoGroup.CameraPair] = set(
        [
            StereoGroup.CameraPair(camera.master, camera)
            for camera in chunk.cameras
            if camera.master != camera
        ]
    )
    return stereo_cameras


def _group_stereo_data(
    sensor_pair: StereoGroup.SensorPair,
    camera_pairs: Iterable[StereoGroup.CameraPair],
) -> StereoGroup:
    """Groups stereo sensors and cameras by matching the camera sensors with the sensor pair."""
    filtered_camera_pairs: list[StereoGroup.CameraPair] = [
        camera_pair
        for camera_pair in camera_pairs
        if camera_pair.first.sensor == sensor_pair.first
        and camera_pair.second.sensor == sensor_pair.second
    ]

    return StereoGroup(sensor_pair=sensor_pair, camera_pairs=filtered_camera_pairs)
