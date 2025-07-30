"""Module with math utilities."""

import Metashape as ms
import numpy as np


def matrix_to_array(matrix: ms.Matrix) -> np.ndarray:
    """Converts a Metashape matrix to a numpy array."""
    return np.array(matrix).reshape(matrix.size)


def vector_to_array(vector: ms.Vector) -> np.ndarray:
    """Converts a Metashape vector to a numpy array."""
    return np.array(vector)
