"""Module for reading and writing configurations to file. Supported formats are
JSON, YAML, TOML and MSGPACK."""

from pathlib import Path

import msgspec


def read_config(path: Path, mode: str = "r") -> dict | str:
    """Reads a configuration from file. Supported formats are JSON, TOML, YAML,
    and MSGPACK."""

    match path.suffix:
        case ".json":
            return _read_config_json(path, mode)
        case ".toml":
            return _read_config_toml(path, mode)
        case ".yml" | ".yaml":
            return _read_config_yaml(path, mode)
        case ".msgpack":
            return _read_config_msgpack(path, mode)
        case _:
            return f"invalid configuration file format: {path.suffix}"


def _read_config_json(path: Path, mode: str = "r") -> dict | str:
    """Reads a configuration from a JSON file."""
    try:
        with open(path, mode=mode) as handle:
            data: dict = msgspec.json.decode(handle.read())
            return data
    except IOError as error:
        return str(error)


def _read_config_yaml(path: Path, mode: str = "r") -> dict | str:
    """Reads a configuration from a YAML file."""
    try:
        with open(path, mode=mode) as handle:
            data: dict = msgspec.yaml.decode(handle.read())
            return data
    except IOError as error:
        return str(error)


def _read_config_toml(path: Path, mode: str = "r") -> dict | str:
    """Reads a configuration from a TOML file."""
    try:
        with open(path, mode=mode) as handle:
            data: dict = msgspec.toml.decode(handle.read())
            return data
    except IOError as error:
        return str(error)


def _read_config_msgpack(path: Path, mode: str = "r") -> dict | str:
    """Reads a configuration from a MSGPACK file."""
    try:
        with open(path, mode=mode) as handle:
            data: dict = msgspec.msgpack.decode(handle.read())
            return data
    except IOError as error:
        return str(error)


def write_config(path: Path, data: dict, mode: str = "w") -> Path | str:
    """Writes a configuration to file. Supported formats are JSON, TOML, YAML,
    and MSGPACK."""

    match path.suffix:
        case ".json":
            return _write_config_json(data, path, mode)
        case ".toml":
            return _write_config_toml(data, path, mode)
        case ".yml" | ".yaml":
            return _write_config_yaml(data, path, mode)
        case ".msgpack":
            return _write_config_msgpack(data, path, mode)
        case _:
            return f"invalid configuration file format: {path.suffix}"


def _write_config_json(path: Path, data: dict, mode: str = "w") -> Path | str:
    """Writes a configuration to a JSON file."""
    try:
        with open(path, mode) as handle:
            handle.write(msgspec.json.encode(data))
            return path
    except IOError as error:
        return str(error)


def _write_config_yaml(path: Path, data: dict, mode: str = "w") -> Path | str:
    """Writes a configuration to a YAML file."""
    try:
        with open(path, mode) as handle:
            handle.write(msgspec.yaml.encode(data))
            return path
    except IOError as error:
        return str(error)


def _write_config_toml(path: Path, data: dict, mode: str = "w") -> Path | str:
    """Writes a configuration to a TOML file."""
    try:
        with open(path, mode) as handle:
            handle.write(msgspec.toml.encode(data))
            return path
    except IOError as error:
        return str(error)


def _write_config_msgpack(path: Path, data: dict, mode: str = "w") -> Path | str:
    """Writes a configuration to a MSGPACK file."""
    try:
        with open(path, mode) as handle:
            handle.write(msgspec.msgpack.encode(data))
            return path
    except IOError as error:
        return str(error)
