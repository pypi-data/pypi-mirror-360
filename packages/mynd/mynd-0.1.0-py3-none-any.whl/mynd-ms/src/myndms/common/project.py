"""Metashape document functions."""

from pathlib import Path

import Metashape as ms


VALID_DOCUMENT_EXTENSIONS = [".psz", ".psx"]


def create_document() -> ms.Document:
    """Create a metashape document."""
    return ms.Document()


def read_document(path: Path) -> ms.Document | str:
    """Reads the document from the given path."""
    if not path.exists():
        return f"path does not exist: {path}"
    if not path.is_file():
        return f"document path is not a file: {path}"
    if path.suffix not in VALID_DOCUMENT_EXTENSIONS:
        return f"invalid document extension: {path}"

    document: ms.Document = create_document()
    try:
        document.open(str(path))
    except IOError as error:
        return str(error)
    return document


def write_document(document: ms.Document, path: Path = None) -> Path | str:
    """Writes the document to the given path."""
    if not path:
        return save_document_to_path(document, Path(document.path))
    else:
        return save_document_to_path(document, path)


def save_document_to_path(document: ms.Document, path: Path) -> Path | str:
    """Saves the document to the given path."""
    if path.suffix not in VALID_DOCUMENT_EXTENSIONS:
        return f"invalid document extension: {path}"

    try:
        document.save(str(path))
    except OSError as error:
        return str(error)
    return path


def create_chunk(document: ms.Document, label: str = None) -> ms.Chunk:
    """Creates a chunk for the given document."""
    chunk: ms.Chunk = document.addChunk()
    if label:
        chunk.label = label
    return chunk
