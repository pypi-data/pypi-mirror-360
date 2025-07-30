"""Module for runtime environment."""

import os

from dataclasses import dataclass
from pathlib import Path

import dotenv


ROOT_DIR: Path = Path(os.path.dirname(os.path.abspath(__file__))).parents[2]
ENV_PATH: Path = ROOT_DIR / Path(".env")


CACHE_DIR_KEY: str = "CACHE_DIR"
RESOURCE_DIR_KEY: str = "RESOURCE_DIR"
SOURCE_DIR_KEY: str = "SOURCE_DIR"


@dataclass
class Environment:
    """Class representing environment variables."""

    working_directory: Path
    resource_directory: Path
    source_directory: Path
    cache_directory: Path


def load_environment(path: Path = ENV_PATH) -> Environment | str:
    """Loads variables from an environment file."""

    if not path.exists():
        return f"environment file does not exist: {path}"

    variables: dict = dotenv.dotenv_values(path)
    current_directory: Path = Path(os.getcwd())

    if CACHE_DIR_KEY in variables:
        cache_directory: Path = Path(variables.get(CACHE_DIR_KEY))
    else:
        return f"missing environmental variable: {CACHE_DIR_KEY}"

    if RESOURCE_DIR_KEY in variables:
        resource_directory: Path = Path(variables.get(RESOURCE_DIR_KEY))
    else:
        return f"missing environmental variable: {RESOURCE_DIR_KEY}"

    if SOURCE_DIR_KEY in variables:
        source_directory: Path = Path(variables.get(SOURCE_DIR_KEY))
    else:
        return f"missing environmental variable: {SOURCE_DIR_KEY}"

    return Environment(
        cache_directory=cache_directory,
        working_directory=current_directory,
        resource_directory=resource_directory,
        source_directory=source_directory,
    )
