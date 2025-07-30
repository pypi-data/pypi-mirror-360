"""Module for registration utility functionality."""

import numpy as np

from mynd.geometry.transformations import decompose_rigid_transform
from mynd.geometry.transformations import rotation_matrix_to_euler
from mynd.utils.log import logger

from .types import RegistrationResult


def log_registration_result(result: RegistrationResult) -> None:
    """Logs a registration result."""

    scale, rotation, translation = decompose_rigid_transform(result.transformation)

    rotz, roty, rotx = rotation_matrix_to_euler(rotation, degrees=True)

    correspondence_count: int = len(result.correspondence_set)

    np.set_printoptions(precision=3)

    logger.info(f"Corresp.:     {correspondence_count}")
    logger.info(f"Fitness:      {result.fitness:.5f}")
    logger.info(f"Inlier RMSE:  {result.inlier_rmse:.5f}")
    logger.info(f"Scale:        {scale:.3f}")
    logger.info(f"Translation:  {translation}")
    logger.info(f"Rot. ZYX:     {rotz:.2f}, {roty:.2f}, {rotx:.2f}")
