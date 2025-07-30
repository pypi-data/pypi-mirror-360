"""Module with generic generator functions."""

from collections.abc import Iterable
from typing import TypeVar


T: TypeVar = TypeVar("T")


def generate_chunks(items: Iterable[T], max_size: int) -> Iterable[Iterable[T]]:
    """Generate chunks of the items with a given maximum chunk size."""
    for index in range(0, len(items), max_size):
        yield items[index : index + max_size]


def generate_chunked_items(items: Iterable[T], max_size: int) -> Iterable[Iterable[T]]:
    """Generates an iterable of item chunks with a maximum size."""
    return [items[index : index + max_size] for index in range(0, len(items), max_size)]
