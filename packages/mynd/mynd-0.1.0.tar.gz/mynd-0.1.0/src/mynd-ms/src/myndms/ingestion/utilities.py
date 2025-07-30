"""Utility functionality specific for Metashape ingestion package."""

from collections.abc import Iterable
from typing import Any

import Metashape as ms

from mynd.utils.log import logger


def check_uniform_type(items: Iterable[Any]) -> bool:
    """Returns true if all items in the collection are of the same type."""
    item_types: set[type] = set([type(item) for item in items])
    return len(item_types) == 1


def check_all_equal(items: Iterable[Any]) -> bool:
    """Returns true if all items in the collection are the same."""
    template = items[0]
    is_equal: list[bool] = [item == template for item in items]
    return all(is_equal)


def log_sensor(sensor: ms.Sensor) -> None:
    """Logs a Metashape sensor."""
    logger.info(f"Sensor: {sensor}")
    logger.info(f" - Master:        {sensor.master}")
    logger.info(f" - Key:           {sensor.key}")
    logger.info(f" - Data type:     {sensor.data_type}")
    logger.info(f" - Type:          {sensor.type}")
    logger.info(f" - Fix location:  {sensor.fixed_location}")
    logger.info(f" - Fix rotation:  {sensor.fixed_rotation}")
    logger.info(f" - Width:         {sensor.width}")
    logger.info(f" - Height:        {sensor.height}")
    logger.info(f" - Bands:         {sensor.bands}")
    logger.info(f" - Layer index:   {sensor.layer_index}")
    logger.info(f" - Planes:        {sensor.planes}")
    logger.info(f" - Ref. enabled:  {sensor.reference.enabled}")
    logger.info(f" - Ref. loc.:     {sensor.reference.location}")
    logger.info(f" - Ref. rot.:     {sensor.reference.rotation}")
    logger.info(f" - Normalize:     {sensor.normalize_to_float}")
    logger.info(f" - Location:      {sensor.location}")
    logger.info(f" - Rotation:      {sensor.rotation}")
    logger.info(f" - Sensitivity:   {sensor.sensitivity}")
    logger.info(f" - Vignetting:    {sensor.vignetting}")
    logger.info(f" - Film camera:   {sensor.film_camera}")


def log_calibration(calibration: ms.Calibration) -> None:
    """Logs a Metashape calibration."""
    logger.info(f"Calibration:  {calibration}")
    logger.info(f" - Type:      {calibration.type}")
    logger.info(f" - Width:     {calibration.width}")
    logger.info(f" - Height:    {calibration.height}")
    logger.info(f" - Focal:     {calibration.f}")
    logger.info(f" - Cx:        {calibration.cx}")
    logger.info(f" - Cy:        {calibration.cy}")
    logger.info(f" - B1:        {calibration.b1}")
    logger.info(f" - B2:        {calibration.b2}")
    logger.info(f" - K1:        {calibration.k1}")
    logger.info(f" - K2:        {calibration.k2}")
    logger.info(f" - K3:        {calibration.k3}")
    logger.info(f" - K4:        {calibration.k4}")
    logger.info(f" - P1:        {calibration.p1}")
    logger.info(f" - P2:        {calibration.p2}")
    logger.info(f" - P3:        {calibration.p3}")
    logger.info(f" - P4:        {calibration.p4}")
