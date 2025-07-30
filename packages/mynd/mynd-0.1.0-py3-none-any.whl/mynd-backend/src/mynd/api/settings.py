"""Module for application settings."""

from pathlib import Path
from typing import ClassVar, TypeAlias

from pydantic import BaseModel, Field


# Get package root four levels above source file
PACKAGE_ROOT: Path = Path(__file__).parents[3]


DEFAULT_PATHS: dict[str, Path] = {
    "env_file": PACKAGE_ROOT / ".env",
    "resource_directory": PACKAGE_ROOT / "resources",
    "hitnet_model": PACKAGE_ROOT / "resources/hitnet_models/hitnet_eth3d_720x1280.onnx",
}


class DatabaseSettings(BaseModel):
    """Class representing database settings."""

    name: str | None = None
    host: str | None = None
    port: int | None = None


class ImageStoreSettings(BaseModel):
    """Class representing image repository settings."""

    root: Path | None = None
    label_strategy: str = "label_by_stem"
    suffixes: list[str] = [".png", ".jpeg", ".tif", ".tiff"]
    search_depth: int = 1


class StereoSettings(BaseModel):
    """Class representing stereo processing settings."""

    model_file: Path = DEFAULT_PATHS.get("hitnet_model")


class ApplicationDirectories(BaseModel):
    """Class representing application directories."""

    resources: Path = DEFAULT_PATHS.get("resource_directory")
    export: Path | None = None


class ApplicationSettings(BaseModel):
    """Class representing application settings."""

    # Add type alias to ease referencing
    Directories: ClassVar[TypeAlias] = ApplicationDirectories
    Database: ClassVar[TypeAlias] = DatabaseSettings

    app_name: str = "Mynd API"
    verbose: bool = False
    env_file: Path = DEFAULT_PATHS.get("env_file")
    config_file: Path | None = None

    database: DatabaseSettings | None = None
    image_store: ImageStoreSettings | None = None

    directories: Directories = Field(default_factory=Directories)
    stereo: StereoSettings = Field(default_factory=StereoSettings)
