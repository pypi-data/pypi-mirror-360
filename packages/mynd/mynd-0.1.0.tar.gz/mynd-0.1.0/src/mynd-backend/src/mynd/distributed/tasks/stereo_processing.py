"""Module for stereo processing tasks."""

import mynd.models.record as records
import mynd.models.schema as schemas

from mynd.geometry.stereo import (
    PixelMap,
    compute_rectified_sensors,
    compute_rectified_pixel_maps,
)

from mynd.api.server import load_application_database
from mynd.api.settings import ApplicationSettings
from mynd.database import Engine, Session, create_engine
from mynd.distributed.worker import celery_app
from mynd.utils.containers import Pair


@celery_app.task
def process_stereo_rectification(settings: ApplicationSettings, rig_id: int) -> None:
    """Rectifies a stereo rig."""

    engine: Engine = load_application_database(settings)

    with Session(engine) as session:
        stereo_rig: records.StereoRigRecord | None = session.get(
            records.StereoRigRecord, rig_id
        )
        if stereo_rig is None:
            return

        # If the stereo rig already has rectified sensors, we delete them and the
        # corresponding pixel maps
        if stereo_rig.sensors_rectified is not None:
            delete_stereo_rig_rectification(session, stereo_rig)

        assert (
            stereo_rig.sensors_rectified is None
        ), "invalid rectified stereo rig sensors"
        assert stereo_rig.pixel_maps is None, "invalid rectified stereo rig pixel maps"

        stereo_rig: records.StereoRigRecord = compute_stereo_rig_rectification(
            session, stereo_rig
        )


def delete_stereo_rig_rectification(
    session: Session, stereo_rig: records.StereoRigRecord
) -> None:
    """Deletes the rectified sensors and pixel maps for a stereo rig."""
    sensors_rectified: records.StereoRigRecord.SensorPair = stereo_rig.sensors_rectified
    stereo_rig.rectified_sensor_pair_id = None

    pixel_maps: records.StereoRigRecord.PixelMapPair = stereo_rig.pixel_maps
    stereo_rig.pixel_map_id = None

    session.delete(sensors_rectified)
    session.delete(pixel_maps)

    session.commit()
    session.refresh(stereo_rig)


def compute_stereo_rig_rectification(
    session: Session, stereo_rig: records.StereoRigRecord
) -> records.StereoRigRecord:
    """Computes rectified sensors and pixel maps for a stereo rig."""

    # Create new rectified sensors
    rectified_sensors: schemas.StereoRigSchema.SensorPair = compute_rectified_sensors(
        schemas.StereoRigSchema.SensorPair.model_validate(stereo_rig.sensors)
    )

    # Update rectified sensors for stereo rig
    stereo_rig.sensors_rectified: records.StereoRigRecord.SensorPair = (
        convert_sensor_pair_schema_to_record(rectified_sensors)
    )

    # Update sensor pair chunks
    stereo_rig.sensors.chunk = stereo_rig.chunk
    stereo_rig.sensors_rectified.chunk = stereo_rig.chunk

    pixel_maps: Pair[PixelMap]
    pixel_maps, _ = compute_rectified_pixel_maps(
        sensors=convert_sensor_pair_record_to_schema(stereo_rig.sensors),
        sensors_rectified=convert_sensor_pair_record_to_schema(
            stereo_rig.sensors_rectified
        ),
    )

    stereo_rig.pixel_maps: records.StereoRigRecord.PixelMapPair = (
        records.StereoRigRecord.PixelMapPair(
            master=records.PixelMapRecord(values=pixel_maps.first.to_array().tolist()),
            slave=records.PixelMapRecord(values=pixel_maps.second.to_array().tolist()),
        )
    )

    session.add(stereo_rig)
    session.commit()
    session.refresh(stereo_rig)

    return stereo_rig


def convert_to_stereo_rig_with_maps(
    record: records.StereoRigRecord,
) -> schemas.StereoRigWithMapsSchema:
    """Converts a stereo rig record to a stereo rig with pixel maps."""
    raise NotImplementedError


def convert_sensor_pair_schema_to_record(
    sensor_pair: schemas.StereoRigSchema.SensorPair,
) -> records.StereoRigRecord.SensorPair:
    """Converts a sensor pair data model to a storage model."""
    sensor_pair_data: dict = sensor_pair.model_dump()
    sensor_pair_storage: records.StereoRigRecord.SensorPair = (
        records.StereoRigRecord.SensorPair.model_validate(sensor_pair_data)
    )
    sensor_pair_storage.master = convert_sensor_schema_to_record(sensor_pair.master)
    sensor_pair_storage.slave = convert_sensor_schema_to_record(sensor_pair.slave)
    return sensor_pair_storage


def convert_sensor_schema_to_record(
    sensor: schemas.SensorSchema,
) -> records.SensorRecord:
    """Converts a sensor data model to a storage model."""
    sensor_data: dict = sensor.model_dump()
    sensor_storage: records.SensorRecord = records.SensorRecord.model_validate(
        sensor_data
    )
    sensor_storage.calibration = convert_calibration_schema_to_record(
        sensor.calibration
    )
    return sensor_storage


def convert_calibration_schema_to_record(
    calibration: schemas.CalibrationSchema,
) -> records.CalibrationRecord:
    """Converts a calibration data model to a storage model."""
    calibration_data: dict = calibration.model_dump()
    return records.CalibrationRecord.model_validate(calibration_data)


def convert_sensor_pair_record_to_schema(
    record: records.StereoRigRecord.SensorPair,
) -> schemas.StereoRigSchema.SensorPair:
    """Converts a stereo sensor storage model to a data model."""
    sensor_pair_data: dict = record.model_dump()
    sensor_pair_data["master"] = convert_sensor_record_to_schema(record.master)
    sensor_pair_data["slave"] = convert_sensor_record_to_schema(record.slave)
    return schemas.StereoRigSchema.SensorPair.model_validate(sensor_pair_data)


def convert_sensor_record_to_schema(
    record: records.SensorRecord,
) -> schemas.SensorSchema:
    """Converts a sensor model to a sensor."""
    sensor_data: dict = record.model_dump()
    sensor_data["calibration"] = convert_calibration_record_to_schema(
        record.calibration
    )
    return schemas.SensorSchema.model_validate(sensor_data)


def convert_calibration_record_to_schema(
    record: records.CalibrationRecord,
) -> schemas.CalibrationSchema:
    """Converts a calibration model to a data model."""
    calibration_data: dict = record.model_dump()
    return schemas.CalibrationSchema.model_validate(calibration_data)
