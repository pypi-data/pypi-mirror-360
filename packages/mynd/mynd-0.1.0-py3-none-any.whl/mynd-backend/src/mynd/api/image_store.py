"""Module for image store."""

import concurrent
import functools
import typing

from pathlib import Path

from pydantic import BaseModel, Field

from mynd.utils.filesystem import walk_directory


class FileGroupConfig(BaseModel):
    """Class representing a file group config."""

    name: str
    root: Path
    suffixes: list[str] | None = None


@functools.lru_cache
def compute_filemap_by_name(paths: tuple[Path]) -> dict[str, Path]:
    """Computes a mapping from name to path. The function has a cache in order
    to avoid having to recompute the dictionary for every lookup."""
    return {path.name: path for path in paths}


@functools.lru_cache
def compute_filemap_by_stem(paths: tuple[Path]) -> dict[str, Path]:
    """Computes a mapping from stem to path. The function has a cache in order
    to avoid having to recompute the dictionary for every lookup."""
    return {path.stem: path for path in paths}


class FileGroup(BaseModel):
    """Class representing a file group."""

    name: str
    config: FileGroupConfig
    files: list[Path] = Field(default_factory=list)

    @property
    def stem_to_path(self: typing.Self) -> dict[str, Path]:
        """Returns a dictionary mapping path stems to paths."""
        return compute_filemap_by_stem(tuple(self.files))

    @property
    def name_to_path(self: typing.Self) -> dict[str, Path]:
        """Returns a dictionary mapping path names to paths."""
        return compute_filemap_by_name(tuple(self.files))

    def __len__(self: typing.Self) -> int:
        """Returns the number of files in the group."""
        return len(self.files)

    def file_count(self: typing.Self) -> int:
        """Returns the file count for the group."""
        return len(self.files)

    def retrieve_by_stem(self: typing.Self, stem: str) -> Path | None:
        """Retrieves a file by stem."""
        return self.stem_to_path.get(stem)

    def retrieve_by_name(self: typing.Self, name: str) -> Path | None:
        """Retrieves a file by name."""
        return self.name_to_path.get(name)


class ImageStore(BaseModel):
    """Class representing an image store."""

    FileGroupConfig: typing.ClassVar[typing.TypeAlias] = FileGroupConfig
    FileGroup: typing.ClassVar[typing.TypeAlias] = FileGroup

    file_groups: list[FileGroup] = Field(default_factory=list)

    def __contains__(self: typing.Self, group_name: str) -> bool:
        """Returns true if the key is in the repository."""
        return group_name in [group.name for group in self.file_groups]

    def total_count(self: typing.Self) -> int:
        """Returns the total file count in the image store."""
        return sum([len(group) for group in self.file_groups])

    def group_count(self: typing.Self) -> dict[str, int]:
        """Returns the file count for each group."""
        return {group.name: len(group) for group in self.file_groups}

    def group_names(self: typing.Self) -> list[str]:
        """Returns the group names in the file store."""
        return [group.name for group in self.file_groups]

    def get_group(self: typing.Self, group_name: str) -> FileGroup | None:
        """Returns the file group by group name."""
        lookup: dict = {group.name: group for group in self.file_groups}
        return lookup.get(group_name)

    def iter_groups(self: typing.Self) -> typing.Iterator[FileGroup]:
        """Iterates of the file groups."""
        for group in self.file_groups:
            yield group


def create_image_store(config: dict) -> ImageStore:
    """Creates an image store by searching files from a root directory."""
    file_group_configs: list[FileGroupConfig] = [
        create_file_group_config(**item) for item in config.get("file_groups")
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        file_groups: list[FileGroup] = list(
            executor.map(create_file_group, file_group_configs)
        )

    return ImageStore(file_groups=file_groups)


def create_file_group_config(
    name: str, directory: Path, suffixes: list[str]
) -> FileGroupConfig:
    """Creates a file group configuration from a dictionary."""
    return FileGroupConfig(name=name, root=directory, suffixes=suffixes)


def create_file_group(config: FileGroupConfig) -> FileGroup:
    """Creates a file group with the given configuration and label strategy."""
    contents: list[Path] = walk_directory(config.root)
    files: list[Path] = [path for path in contents if path.is_file()]
    if config.suffixes:
        files: list[Path] = [path for path in files if path.suffix in config.suffixes]
    return FileGroup(name=config.name, config=config, files=files)
