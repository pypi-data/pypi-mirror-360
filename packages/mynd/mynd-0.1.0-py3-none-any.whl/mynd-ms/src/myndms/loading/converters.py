"""Module with converter functions from Metashape to Mynds record models."""

from pathlib import Path

import Metashape as ms

import mynd.models.record as records

from myndms.common.math import matrix_to_array, vector_to_array
from myndms.helpers import get_camera_metadata
from myndms.helpers import get_camera_reference_estimate
from myndms.helpers import get_camera_reference_prior
from myndms.helpers import CalibrationOpenCV, convert_calibration_to_opencv


def convert_sensor_to_orm(sensor: ms.Sensor) -> records.SensorRecord:
    """Converts a Metashape sensor to an ORM sensor model."""

    calibration_model: records.CalibrationRecord = _convert_calibration_to_orm(
        sensor.calibration
    )

    location: list[float] = vector_to_array(
        sensor.location * sensor.chunk.transform.scale
    ).tolist()
    rotation: list[list[float]] = matrix_to_array(sensor.rotation).T

    return records.SensorRecord(
        label=sensor.label,
        width=sensor.width,
        height=sensor.height,
        location=location,
        rotation=rotation,
        calibration=calibration_model,
    )


def convert_camera_to_orm(camera: ms.Camera) -> records.CameraRecord:
    """Converts a Metashape camera to an ORM camera model."""

    metadata: dict = get_camera_metadata(camera)
    camera_model: records.CameraRecord = records.CameraRecord(
        label=camera.label,
        image_label=Path(camera.photo.path).stem,
        readings=metadata,
    )

    prior_reference: records.PriorReferenceRecord | None = (
        _convert_prior_reference_to_orm(camera)
    )
    aligned_reference: records.AlignedReferenceRecord | None = (
        _convert_aligned_reference_to_orm(camera)
    )

    if prior_reference is not None:
        camera_model.prior_reference = prior_reference

    if aligned_reference is not None:
        camera_model.aligned_reference = aligned_reference

    return camera_model


"""
Helper functions:
    _convert_calibration_to_orm
    _convert_aligned_reference_to_orm
    _convert_prior_reference_to_orm
"""


def _convert_calibration_to_orm(
    calibration: ms.Calibration,
) -> records.CalibrationRecord:
    """Converts a calibration to an ORM calibration model."""
    opencv_calibration: CalibrationOpenCV = convert_calibration_to_opencv(calibration)
    return records.CalibrationRecord(**opencv_calibration.to_dict())


def _convert_aligned_reference_to_orm(
    camera: ms.Camera,
) -> records.AlignedReferenceRecord | None:
    """Converts an aligned camera reference to an ORM reference model."""

    if camera.transform is None:
        return None

    epsg_code: int = int(camera.chunk.camera_crs.authority.lstrip("EPSG::"))
    reference: dict | None = get_camera_reference_estimate(camera)

    return records.AlignedReferenceRecord(
        epsg_code=epsg_code,
        longitude=reference.get("longitude"),
        latitude=reference.get("latitude"),
        height=reference.get("height"),
        yaw=reference.get("yaw"),
        pitch=reference.get("pitch"),
        roll=reference.get("roll"),
    )


def _convert_prior_reference_to_orm(
    camera: ms.Camera,
) -> records.PriorReferenceRecord | None:
    """Converts a prior camera reference to an ORM reference model."""

    if not camera.reference.enabled:
        return None

    epsg_code: int = int(camera.chunk.camera_crs.authority.lstrip("EPSG::"))
    reference: dict | None = get_camera_reference_prior(camera)

    return records.PriorReferenceRecord(
        epsg_code=epsg_code,
        longitude=reference.get("longitude"),
        latitude=reference.get("latitude"),
        height=reference.get("height"),
        yaw=reference.get("yaw"),
        pitch=reference.get("pitch"),
        roll=reference.get("roll"),
    )
