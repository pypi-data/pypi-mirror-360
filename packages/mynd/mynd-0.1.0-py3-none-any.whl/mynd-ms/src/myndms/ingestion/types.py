"""Module for ingestion data types."""

from dataclasses import dataclass, field, asdict
from typing import ClassVar

import Metashape as ms


@dataclass
class SensorConfig:
    """Class representing a sensor config."""

    @dataclass
    class Calibration:
        """Class representing a sensor calibration."""

        width: int
        height: int

        f: float

        cx: float = 0.0
        cy: float = 0.0

        b1: float = 0.0
        b2: float = 0.0

        k1: float = 0.0
        k2: float = 0.0
        k3: float = 0.0
        k4: float = 0.0

        p1: float = 0.0
        p2: float = 0.0
        p3: float = 0.0
        p4: float = 0.0

        def to_dict(self) -> dict:
            """Returns a dictionary representation of the object."""
            return asdict(self)

    label: str
    camera_column: str
    master: bool

    fixed_params: list[str] = field(default_factory=list)

    fixed_location: bool = True
    fixed_rotation: bool = True

    location: list[float] | None = None
    rotation: list[float] | None = None

    location_accuracy: list[float] | None = None
    rotation_accuracy: list[float] | None = None

    calibration: Calibration | None = None


@dataclass
class ReferenceConfig:
    """Class representing a reference config."""

    LABEL_KEY: ClassVar[str] = "label"
    LOCATION_KEYS: ClassVar[list[str]] = ["longitude", "latitude", "height"]
    ROTATION_KEYS: ClassVar[list[str]] = ["yaw", "pitch", "roll"]

    crs: str
    columns: dict
    constants: dict

    @property
    def keys(self) -> list[str]:
        return [self.LABEL_KEY] + self.LOCATION_KEYS + self.ROTATION_KEYS

    @property
    def label_key(self) -> str:
        """Return the label key for the reference configuration."""
        return self.LABEL_KEY

    @property
    def location_keys(self) -> list[str]:
        """Returns the location keys for the reference configuration."""
        return self.LOCATION_KEYS

    @property
    def rotation_keys(self) -> list[str]:
        """Returns the rotation keys for the reference configuration."""
        return self.ROTATION_KEYS

    @property
    def label_column(self) -> str:
        """Returns the label column for the reference configuration."""
        return self.columns.get(self.LABEL_KEY)

    @property
    def location_columns(self) -> list[str]:
        """Returns the location columns for the reference configuration."""
        return [self.columns.get(key) for key in self.LOCATION_KEYS]

    @property
    def rotation_columns(self) -> list[str]:
        """Returns the rotation columns for the reference configuration."""
        return [self.columns.get(key) for key in self.ROTATION_KEYS]


@dataclass
class IngestionConfig:
    """Class representing a configuration manager."""

    sensors: list[SensorConfig]
    reference: ReferenceConfig

    def get_camera_columns(self) -> list[str]:
        """Gets the camera columns from the sensor configurations."""
        return [config.camera_column for config in self.sensors]


@dataclass
class CameraReader:
    """Class representing a camera reader."""

    entries: dict[str, ms.Sensor]

    @property
    def columns(self) -> list[str]:
        """The pname property."""
        return list(self.entries.keys())

    @property
    def sensors(self) -> list[ms.Sensor]:
        """Returns the sensors in the camera reader."""
        return list(self.entries.values())

    def get_sensor_map(self) -> dict[str, ms.Sensor]:
        """Returns the mapping from column to sensor."""
        return self.entries

    def get_sensor(self, key: str) -> ms.Sensor | None:
        """Returns a sensor if the key is in the reader entries."""
        return self.entries.get(key)
