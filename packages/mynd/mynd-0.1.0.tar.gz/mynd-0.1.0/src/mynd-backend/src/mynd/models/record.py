"""Module for Mynds model models."""

import textwrap

from enum import StrEnum, auto
from typing import ClassVar, Optional, TypeAlias

import numpy as np

from sqlmodel import SQLModel, Column, Field, Relationship
from sqlmodel import Integer, Float, ARRAY, JSON, Enum


class ChunkGroupRecord(SQLModel, table=True):
    """Class representing chunk group record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    chunks: list["ChunkRecord"] = Relationship(back_populates="group")


class ChunkRecord(SQLModel, table=True):
    """Class representing a chunk record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str

    # Create a one-to-many mapping from a chunk group to multiple chunks
    group_id: Optional[int] = Field(default=None, foreign_key="chunkgrouprecord.id")
    group: Optional["ChunkGroupRecord"] = Relationship(back_populates="chunks")

    sensors: list["SensorRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    cameras: list["CameraRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    stereo_rigs: list["StereoRigRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    stereo_sensor_pairs: list["StereoSensorPairRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    stereo_camera_pairs: list["StereoCameraPairRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    camera_tracks: list["CameraTrackRecord"] = Relationship(back_populates="chunk")
    stereo_camera_tracks: list["StereoCameraTrackRecord"] = Relationship(
        back_populates="chunk"
    )


class CameraTrackRecord(SQLModel, table=True):
    """Class representing a camera track."""

    id: Optional[int] = Field(default=None, primary_key=True)
    cameras: list["CameraRecord"] = Relationship(back_populates="track")

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="camera_tracks")


class CalibrationRecord(SQLModel, table=True):
    """Class representing a calibration record.

    For reference:
    https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    width: int
    height: int
    fx: float
    fy: float
    cx: float  # optical center as per OpenCV
    cy: float  # optical center as per OpenCV
    k1: float  # radial distortion as per OpenCV
    k2: float  # radial distortion as per OpenCV
    k3: float  # radial distortion as per OpenCV
    p1: float  # tangential distortion as per OpenCV
    p2: float  # tangential distortion as per OpenCV

    # Create a one-to-one mapping between a sensor and a calibration
    sensor: "SensorRecord" = Relationship(
        back_populates="calibration",
        sa_relationship_kwargs={"uselist": False},
    )


class SensorRecord(SQLModel, table=True):
    """Class representing sensor record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    width: int
    height: int

    location: Optional[list[float]] = Field(
        default=None, sa_column=Column(ARRAY(Float, dimensions=1))
    )
    rotation: Optional[list[list[float]]] = Field(
        default=None, sa_column=Column(ARRAY(Float, dimensions=2))
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="sensors")

    # Create a one-to-one mapping between sensor and calibration
    calibration_id: Optional[int] = Field(
        default=None, foreign_key="calibrationrecord.id"
    )
    calibration: Optional["CalibrationRecord"] = Relationship(
        back_populates="sensor",
        sa_relationship_kwargs={"uselist": False},
    )


class BaseReferenceRecord(SQLModel):
    """Class representing a base reference record."""

    epsg_code: int
    longitude: float
    latitude: float
    height: float
    yaw: float
    pitch: float
    roll: float


class PriorReferenceRecord(BaseReferenceRecord, table=True):
    """Class representing a prior camera reference record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    camera_id: Optional[int] = Field(
        default=None, foreign_key="camerarecord.id", unique=True
    )
    camera: Optional["CameraRecord"] = Relationship(
        back_populates="prior_reference",
        sa_relationship_kwargs={"lazy": "select"},
    )


class AlignedReferenceRecord(BaseReferenceRecord, table=True):
    """Class representing an aligned camera reference record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    camera_id: Optional[int] = Field(
        default=None, foreign_key="camerarecord.id", unique=True
    )
    camera: Optional["CameraRecord"] = Relationship(
        back_populates="aligned_reference",
        sa_relationship_kwargs={"lazy": "select"},
    )


class InterpolatedReferenceRecord(BaseReferenceRecord, table=True):
    """Class representing an interpolated camera reference record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    camera_id: Optional[int] = Field(
        default=None, foreign_key="camerarecord.id", unique=True
    )
    camera: Optional["CameraRecord"] = Relationship(
        back_populates="interpolated_reference",
        sa_relationship_kwargs={"lazy": "select"},
    )


JSONFields: TypeAlias = dict[str, str | float | int | bool]


class CameraRecord(SQLModel, table=True):
    """Class representing a camera record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    image_label: str
    readings: Optional[JSONFields] = Field(default=None, sa_column=Column(JSON))

    track_id: Optional[int] = Field(default=None, foreign_key="cameratrackrecord.id")
    track: Optional["CameraTrackRecord"] = Relationship(back_populates="cameras")

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="cameras")

    # Every camera has a sensor
    sensor_id: Optional[int] = Field(default=None, foreign_key="sensorrecord.id")
    sensor: Optional["SensorRecord"] = Relationship(
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": lambda: CameraRecord.sensor_id == SensorRecord.id,
        }
    )

    prior_reference: Optional["PriorReferenceRecord"] = Relationship(
        back_populates="camera",
        sa_relationship_kwargs={"lazy": "select"},
    )
    aligned_reference: Optional["AlignedReferenceRecord"] = Relationship(
        back_populates="camera",
        sa_relationship_kwargs={"lazy": "select"},
    )
    interpolated_reference: Optional["InterpolatedReferenceRecord"] = Relationship(
        back_populates="camera",
        sa_relationship_kwargs={"lazy": "select"},
    )


class PixelMapRecord(SQLModel, table=True):
    """Class representing a pixel map record. The pixel map value is stored as
    a HxWx2 array with the X- and Y-coordinate mapping, respectively."""

    id: Optional[int] = Field(default=None, primary_key=True)
    values: list[list[list[float]]] = Field(
        sa_column=Column(ARRAY(Float, dimensions=3))
    )

    @property
    def height(self) -> int:
        """Returns the height of the pixel map."""
        return len(self.values)

    @property
    def width(self) -> int:
        """Returns the width of the pixel map."""
        return len(self.values[0])

    def to_array(self) -> np.ndarray:
        """Returns the pixel map as a numpy array."""
        return np.array(self.values).astype(np.float32)


"""
Stereo record models:
 - StereoSensorPairRecord
 - StereoCameraPairRecord
 - StereoPixelMapRecord
 - StereoRigRecord
 - StereoCameraTrackRecord
"""


class StereoSensorPairRecord(SQLModel, table=True):
    """Class representing a stereo sensor pair record. A stereo sensor links
    two sensor records. The stereo sensors is identified by the ids of the two
    sensors, and is owned by a chunk."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # A stereo sensor is uniquely identified by the two sensor ids
    master_id: int = Field(default=None, foreign_key="sensorrecord.id", unique=True)
    master: SensorRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": lambda: StereoSensorPairRecord.master_id == SensorRecord.id,
        }
    )

    slave_id: int = Field(default=None, foreign_key="sensorrecord.id", unique=True)
    slave: SensorRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": lambda: StereoSensorPairRecord.slave_id == SensorRecord.id,
        }
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="stereo_sensor_pairs")


class StereoCameraPairRecord(SQLModel, table=True):
    """Class representing a stereo camera pair record. A stereo camera links two
    camera records. The stereo camera is identified by the ids of the two
    cameras, and is owned by a chunk."""

    id: Optional[int] = Field(default=None, primary_key=True)

    master_id: int = Field(foreign_key="camerarecord.id", unique=True)
    master: CameraRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": lambda: StereoCameraPairRecord.master_id == CameraRecord.id
        }
    )

    slave_id: int = Field(foreign_key="camerarecord.id", unique=True)
    slave: CameraRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": lambda: StereoCameraPairRecord.slave_id == CameraRecord.id
        }
    )

    # TODO: Add validation that the two camera sensors are part of the sensor
    stereo_rig_id: Optional[int] = Field(default=None, foreign_key="stereorigrecord.id")
    stereo_rig: Optional["StereoRigRecord"] = Relationship(
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": textwrap.dedent("""
                StereoRigRecord.id == StereoCameraPairRecord.stereo_rig_id
            """),
        }
    )

    stereo_track_id: Optional[int] = Field(
        default=None, foreign_key="stereocameratrackrecord.id"
    )
    stereo_track: Optional["StereoCameraTrackRecord"] = Relationship(
        back_populates="camera_pairs"
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="stereo_camera_pairs")


class StereoPixelMapRecord(SQLModel, table=True):
    """Class representing a record of a pixel map pair."""

    id: Optional[int] = Field(default=None, primary_key=True)

    master_id: int = Field(default=None, foreign_key="pixelmaprecord.id", unique=True)
    master: PixelMapRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": lambda: StereoPixelMapRecord.master_id == PixelMapRecord.id,
        }
    )

    slave_id: int = Field(default=None, foreign_key="pixelmaprecord.id", unique=True)
    slave: PixelMapRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": lambda: StereoPixelMapRecord.slave_id == PixelMapRecord.id,
        }
    )


class StereoRigRecord(SQLModel, table=True):
    """Class representing a stereo rig record. A stereo rig contains the sensor
    records for the physical sensor system, and the sensor records for the
    virtual/rectified sensor system, including the pixel map between the two
    sensor."""

    SensorPair: ClassVar[TypeAlias] = StereoSensorPairRecord
    CameraPair: ClassVar[TypeAlias] = StereoCameraPairRecord
    PixelMapPair: ClassVar[TypeAlias] = StereoPixelMapRecord

    id: Optional[int] = Field(default=None, primary_key=True)

    sensor_pair_id: int = Field(
        foreign_key="stereosensorpairrecord.id",
        unique=True,
    )
    sensors: StereoSensorPairRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": textwrap.dedent("""
                StereoSensorPairRecord.id == StereoRigRecord.sensor_pair_id
            """),
        }
    )

    camera_pairs: list["StereoCameraPairRecord"] = Relationship(
        back_populates="stereo_rig"
    )

    rectified_sensor_pair_id: Optional[int] = Field(
        default=None,
        foreign_key="stereosensorpairrecord.id",
        unique=True,
    )
    sensors_rectified: Optional["StereoSensorPairRecord"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": textwrap.dedent("""
                StereoSensorPairRecord.id == StereoRigRecord.rectified_sensor_pair_id
            """),
        },
    )

    pixel_map_id: Optional[int] = Field(
        default=None,
        foreign_key="stereopixelmaprecord.id",
        unique=True,
    )
    pixel_maps: Optional["StereoPixelMapRecord"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": textwrap.dedent("""
                StereoPixelMapRecord.id == StereoRigRecord.pixel_map_id
            """),
        }
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="stereo_rigs")


class StereoCameraTrackRecord(SQLModel, table=True):
    """Class representing a stereo camera track."""

    id: Optional[int] = Field(default=None, primary_key=True)
    camera_pairs: list["StereoCameraPairRecord"] = Relationship(
        back_populates="stereo_track"
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="stereo_camera_tracks")
