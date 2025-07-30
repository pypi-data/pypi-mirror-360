"""Module for handling ingestion calls."""

from pathlib import Path
from typing import Any, TypeAlias

import Metashape as ms
import polars as pl

from mynd.utils.log import logger

from .types import SensorConfig
from .types import ReferenceConfig
from .types import IngestionConfig
from .types import CameraReader

from .utilities import log_calibration
from .utilities import log_sensor


def handle_camera_ingestion(
    chunk: ms.Chunk,
    data_frame: pl.DataFrame,
    photos: list[Path],
    config: dict,
) -> ms.Chunk:
    """Handles a camera ingest request.

    :arg document:      target document
    :arg label:         chunk label
    :arg data:          camera + reference table
    :arg images:        image file paths
    :arg config:        ingestion config
    """

    # TODO: Add chunk and camera CRS to config
    chunk.crs = ms.CoordinateSystem("EPSG::4326")

    photo_map: dict[str, Path] = {path.stem: path for path in photos}

    # Convert configuration to dataclasses to ease access
    config: IngestionConfig = create_ingestion_config(config)

    # Create sensors based on the given configuration
    sensors: list[ms.Sensor] = create_sensors(chunk, config.sensors)

    # Create a camera reader from the sensor and sensor configs
    reader: CameraReader = create_camera_reader(sensors, config.sensors)

    # Read multiple cameras for each row in a data frame
    cameras: list[ms.Camera] = read_cameras(chunk, data_frame, reader)

    # Add camera photos
    add_camera_photos(cameras, photo_map)

    # Infer sensor attributes based on photo attributes
    infer_sensor_attributes(chunk)

    # Add camera references
    add_camera_references(chunk, data_frame, config.reference)

    # for sensor in sensors:
    # log_sensor(sensor)

    return chunk


def create_ingestion_config(config: dict) -> IngestionConfig:
    """Creates a manager for the given configuration."""
    sensor_configs: list[SensorConfig] = [
        create_sensor_config(item) for item in config.get("sensors")
    ]
    reference_config = ReferenceConfig(**config.get("reference"))
    return IngestionConfig(sensors=sensor_configs, reference=reference_config)


def create_sensor_config(entries: dict) -> SensorConfig:
    """Creates a sensor configurration from a dictionary."""
    calibration_config: dict | None = entries.pop("calibration", None)
    if calibration_config:
        calibration: SensorConfig.Calibration = SensorConfig.Calibration(
            **calibration_config,
        )
    else:
        calibration = None

    sensor_config = SensorConfig(**entries)
    sensor_config.calibration = calibration
    return sensor_config


def create_sensors(chunk: ms.Chunk, configs: list[SensorConfig]) -> list[ms.Sensor]:
    """Create sensors."""

    sensor_labels: list[str] = [config.label for config in configs]
    is_master: list[bool] = [config.master for config in configs]

    assert len(set(sensor_labels)) == len(sensor_labels), "sensor labels must be unique"
    assert sum(is_master) == 1, "one sensor must be master"

    master: ms.Sensor | None = None
    slaves: list[ms.Sensor] = list()

    for config in configs:
        sensor: ms.Sensor = chunk.addSensor()
        sensor: ms.Sensor = _configure_sensor_attributes(sensor, config)

        if config.master:
            master = sensor
        else:
            slaves.append(sensor)

    assert master is not None, "missing master sensor"

    for slave in slaves:
        slave.master = master

    master.makeMaster()

    for index, sensor in enumerate(master.planes):
        sensor.layer_index = index

    return master.planes


def _configure_sensor_attributes(sensor: ms.Sensor, config: SensorConfig) -> ms.Sensor:
    """Configures a Metashape sensor according to the given configuration."""

    sensor.label = config.label
    sensor.fixed_location = config.fixed_location
    sensor.fixed_rotation = config.fixed_rotation
    sensor.fixed_params = config.fixed_params

    if config.calibration is not None:
        calibration: ms.Calibration = _configure_sensor_calibration(
            ms.Calibration(), config.calibration
        )
        sensor.user_calib = calibration

    if config.location:
        sensor.reference.location = ms.Vector(config.location)
        sensor.reference.enabled = True
        sensor.reference.location_enabled = True

    if config.rotation:
        sensor.reference.rotation = ms.Vector(config.rotation)
        sensor.reference.rotation_enabled = True

    if config.location_accuracy:
        sensor.reference.location_accuracy = ms.Vector(config.location_accuracy)

    if config.rotation_accuracy:
        sensor.reference.rotation_accuracy = ms.Vector(config.rotation_accuracy)

    return sensor


def _configure_sensor_calibration(
    calibration: ms.Calibration,
    config: SensorConfig.Calibration,
) -> ms.Calibration:
    """Configures a Metashape calibration according to the given configuration."""
    calibration.width = config.width
    calibration.height = config.height

    calibration.f = config.f
    calibration.cx = config.cx
    calibration.cy = config.cy

    calibration.b1 = config.b1
    calibration.b2 = config.b2

    calibration.k1 = config.k1
    calibration.k2 = config.k2
    calibration.k3 = config.k3
    calibration.k4 = config.k4

    calibration.p1 = config.p1
    calibration.p2 = config.p2
    calibration.p3 = config.p3
    calibration.p4 = config.p4

    return calibration


def create_camera_reader(
    sensors: list[ms.Sensor], configs: list[SensorConfig]
) -> CameraReader:
    """Creates a camera reader for the given sensors and configurations.
    The reader is created by mapping sensor labels to camera columns in the
    configuration."""

    # In order to map sensors to configs, we create a mapping from label to config
    config_map: dict[str, SensorConfig] = {config.label: config for config in configs}
    sensor_labels: list[str] = [sensor.label for sensor in sensors]

    for key in sensor_labels:
        assert key in config_map, f"missing configuration for sensor: {key}"

    column_to_sensor: dict[str, ms.Sensor] = dict()
    for sensor in sensors:
        config: SensorConfig | None = config_map.get(sensor.label)
        column_to_sensor[config.camera_column] = sensor

    return CameraReader(column_to_sensor)


def read_cameras(
    chunk: ms.Chunk, df: pl.DataFrame, reader: CameraReader
) -> list[ms.Camera]:
    """Read cameras from a data frame."""

    is_master: list[bool] = [sensor.master == sensor for sensor in reader.sensors]
    master_sensors: list[ms.Sensor] = [sensor.master for sensor in reader.sensors]

    assert sum(is_master) == 1, "only one sensor can be master"
    assert len(set(master_sensors)), "all sensors must have the same master"

    for column in reader.columns:
        assert column in df.columns, f"missing column: {column}"

    cameras: list[ms.Camera] = list()

    row: dict[str, Any]
    for row in df.iter_rows(named=True):
        row_cameras: list[ms.Camera] = list()

        for column in reader.columns:
            label: str | None = row.get(column)
            sensor: ms.Sensor | None = reader.get_sensor(column)

            assert label is not None, f'missing label for column "{column}"'
            assert sensor is not None, f'missing sensor for column "{column}"'

            camera: ms.Camera = chunk.addCamera(sensor)
            camera.label = label

            row_cameras.append(camera)

        configured_cameras: list[ms.Camera] = _assign_master_camera_by_sensor(
            row_cameras
        )
        cameras.extend(configured_cameras)

    return cameras


def _assign_master_camera_by_sensor(cameras: list[ms.Camera]) -> list[ms.Camera]:
    """Assigns a master among the cameras based on the master-slave relationship
    of their sensors."""

    has_master_sensor: list[ms.Camera] = [
        camera.sensor == camera.master.sensor for camera in cameras
    ]

    assert len(set(has_master_sensor)) == 1, "only one camera sensor can be master"

    master_camera: ms.Camera = None
    for camera in cameras:
        if camera.sensor == camera.sensor.master:
            master_camera: ms.Camera = camera

    assert master_camera is not None, "no camera with master sensor"

    for camera in cameras:
        camera.master = master_camera

    return cameras


def add_camera_photos(
    cameras: list[ms.Camera], photos: dict[str, Path]
) -> list[ms.Camera]:
    """Adds photos to cameras with labels matching the photo stem, i.e. file
    name with extenstion."""

    assigned_cameras: list[ms.Camera] = list()
    for camera in cameras:
        path: Path | None = photos.get(camera.label)
        if path is None:
            logger.warning(f"missing photo for camera: {camera.label}")

        photo: ms.Photo = ms.Photo()
        photo.path = str(path)
        camera.photo = photo

        assigned_cameras.append(camera)

    return assigned_cameras


def infer_sensor_attributes(chunk: ms.Chunk) -> None:
    """Infers the sensor attributes based on data from camera photos."""

    sensor_cameras: dict[ms.Sensor, list[ms.Camera]] = {
        sensor: list() for sensor in chunk.sensors
    }

    for camera in chunk.cameras:
        sensor_cameras[camera.sensor].append(camera)

    DATA_TYPES: dict[str, ms.DataType] = {
        "I8": ms.DataType.DataType8i,
        "U8": ms.DataType.DataType8u,
        "I16": ms.DataType.DataType16i,
        "U16": ms.DataType.DataType16u,
        "F16": ms.DataType.DataType16f,
        "I32": ms.DataType.DataType32i,
        "U32": ms.DataType.DataType32u,
        "F32": ms.DataType.DataType32f,
        "I64": ms.DataType.DataType64i,
        "U64": ms.DataType.DataType64u,
        "F64": ms.DataType.DataType64f,
    }

    CHANNEL_COUNT_TO_BANDS: dict[str, list[str]] = {
        1: ["Gray"],
        3: ["Red", "Green", "Blue"],
        4: ["Red", "Green", "Blue", "Alpha"],
    }

    for sensor, cameras in sensor_cameras.items():
        image: ms.Image = cameras[0].image()

        data_type: ms.DataType = DATA_TYPES.get(
            image.data_type, ms.DataType.DataTypeUndefined
        )

        bands: list[str] = CHANNEL_COUNT_TO_BANDS.get(image.cn, [])

        sensor.width = image.width
        sensor.height = image.height
        sensor.data_type = data_type
        sensor.bands = bands


def add_camera_references(
    chunk: ms.Chunk,
    df: pl.DataFrame,
    config: ReferenceConfig,
) -> list[ms.Camera]:
    """Add references to cameras in a chunk."""

    chunk.camera_crs = ms.CoordinateSystem(config.crs)

    camera_map: dict[str, ms.Camera] = {
        camera.label: camera for camera in chunk.cameras
    }

    columns: dict[str, str] = {key: config.columns.get(key) for key in config.keys}

    configured_cameras: list[ms.Camera] = list()
    for row in df.iter_rows(named=True):
        # To be able to generalize the rest of the workflow, we map columns to keys
        values: dict[str, Any] = {
            key: row.get(column) for key, column in columns.items()
        }

        label: str = values.get(config.label_key)

        if label not in camera_map:
            logger.warning(f"missing camera: {label}")
            continue

        camera: ms.Camera = camera_map.get(label)
        camera.reference.enabled = True

        camera.reference.location = ms.Vector(
            [values.get(key) for key in config.location_keys]
        )
        camera.reference.location_enabled = True

        camera.reference.rotation = ms.Vector(
            [values.get(key) for key in config.rotation_keys]
        )
        camera.reference.rotation_enabled = True

        location_accuracy: list | None = config.constants.get("location_accuracy")
        rotation_accuracy: list | None = config.constants.get("rotation_accuracy")

        if location_accuracy is not None:
            camera.reference.location_accuracy = ms.Vector(location_accuracy)

        if rotation_accuracy is not None:
            camera.reference.rotation_accuracy = ms.Vector(rotation_accuracy)

        configured_cameras.append(camera)

    return configured_cameras
