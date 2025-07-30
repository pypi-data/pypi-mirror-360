"""Module with helper functionality for reference data."""

import Metashape as ms
import polars as pl


def tabulate_camera_references_estimate(chunk: ms.Chunk) -> pl.DataFrame:
    """Returns a table of estimated camera references from a chunk."""

    items: list[dict] = list()
    for camera in chunk.cameras:
        item: dict | None = get_camera_reference_estimate(camera)
        if item is None:
            continue
        items.append(item)

    return pl.from_dicts(items)


def get_camera_reference_estimate(camera: ms.Camera) -> dict | None:
    """Returns the estimated reference for a camera."""
    if camera.transform is None:
        return None

    assert (
        camera.chunk.camera_crs.authority == "EPSG::4326"
    ), "only epsg 4326 (i.e. WGS84) is supported"

    data: dict = {
        "camera_key": camera.key,
        "camera_label": camera.label,
    }

    reference: tuple | None = _compute_camera_reference_estimate(camera)

    if reference is None:
        return None

    location: ms.Vector
    rotation: ms.Vector
    location, rotation = reference

    data["longitude"] = location.x
    data["latitude"] = location.y
    data["height"] = location.z
    data["yaw"] = rotation.x
    data["pitch"] = rotation.y
    data["roll"] = rotation.z

    return data


def tabulate_camera_references_prior(chunk: ms.Chunk) -> pl.DataFrame:
    """Returns a table of prior camera references from a chunk."""

    items: list[dict] = list()
    for camera in chunk.cameras:
        item: dict | None = get_camera_reference_prior(camera)
        if item is None:
            continue
        items.append(item)

    return pl.from_dicts(items)


def get_camera_reference_prior(camera: ms.Camera) -> dict | None:
    """Returns the prior reference for a camera."""

    if not camera.reference.enabled:
        return None

    assert (
        camera.chunk.camera_crs.authority == "EPSG::4326"
    ), "only epsg 4326 (i.e. WGS84) is supported"

    data: dict = {
        "camera_key": camera.key,
        "camera_label": camera.label,
    }

    if camera.reference.location_enabled:
        data["longitude"] = camera.reference.location.x
        data["latitude"] = camera.reference.location.y
        data["height"] = camera.reference.location.z

    if camera.reference.rotation_enabled:
        data["yaw"] = camera.reference.rotation.x
        data["pitch"] = camera.reference.rotation.y
        data["roll"] = camera.reference.rotation.z

    return data


def _compute_camera_reference_estimate(
    camera: ms.Camera,
) -> tuple[ms.Vector, ms.Vector] | None:
    """Computes the estimated reference for the given camera. The function first selects
    a target CRS, a Cartesian CRS, and the transform to use, and then calculates the
    reference with this configuration."""

    # If the camera is not aligned, the rest of the statistics
    if not camera.transform:
        return None

    chunk: ms.Chunk = camera.chunk

    # If the cameras are defined in a datum other than the chunk
    if chunk.camera_crs:
        transform: ms.Matrix = (
            ms.CoordinateSystem.datumTransform(chunk.crs, chunk.camera_crs)
            * chunk.transform.matrix
        )
    else:
        transform: ms.Matrix = chunk.transform.matrix

    # Get ECEF
    transform: ms.Matrix = _get_target_transform(camera)
    target_crs: ms.CoordinateSystem = _get_target_crs(camera)
    cartesian_crs: ms.CoordinateSystem = _get_cartesian_crs(target_crs)

    # Parameters: ecef_crs, target_crs, transform
    estimated_location: ms.Vector
    estimated_rotation: ms.Vector
    estimated_location, estimated_rotation = _compute_reference_estimate(
        camera=camera,
        transform=transform,
        target_crs=target_crs,
        cartesian_crs=cartesian_crs,
    )

    return estimated_location, estimated_rotation


def _compute_reference_estimate(
    camera: ms.Camera,
    transform: ms.Matrix,
    target_crs: ms.CoordinateSystem,
    cartesian_crs: ms.CoordinateSystem,
) -> tuple[ms.Vector, ms.Vector]:
    """Computes the location and rotation for an aligned camera to the target CRS.
    The Cartesian CRS is used as a common intermediate CRS, while the return
    references are converted to the target CRS."""

    # Transformation from camera to ECEF (but without proper rotation)
    camera_transform: ms.Matrix = transform * camera.transform
    antenna_transform: ms.Matrix = _get_antenna_transform(camera.sensor)

    # Compensate for antenna lever arm
    location_ecef: ms.Vector = (
        camera_transform.translation()
        + camera_transform.rotation() * antenna_transform.translation()
    )
    rotation_ecef: ms.Matrix = (
        camera_transform.rotation() * antenna_transform.rotation()
    )

    # Get orientation relative to local frame
    if (
        camera.chunk.euler_angles == ms.EulerAnglesOPK
        or camera.chunk.euler_angles == ms.EulerAnglesPOK
    ):
        localframe: ms.Matrix = target_crs.localframe(location_ecef)
    else:
        localframe: ms.Matrix = cartesian_crs.localframe(location_ecef)

    # Convert the location from Cartesian CRS to target CRS
    estimated_location: ms.Vector = ms.CoordinateSystem.transform(
        location_ecef, cartesian_crs, target_crs
    )

    # Compute estimate rotation as matrix and vector
    estimated_rotation: ms.Vector = ms.utils.mat2euler(
        localframe.rotation() * rotation_ecef, camera.chunk.euler_angles
    )

    return estimated_location, estimated_rotation


def _get_target_transform(camera: ms.Camera) -> ms.Matrix:
    """Returns the target transform for a camera."""
    if camera.chunk.camera_crs:
        transform: ms.Matrix = (
            ms.CoordinateSystem.datumTransform(
                camera.chunk.crs, camera.chunk.camera_crs
            )
            * camera.chunk.transform.matrix
        )
    else:
        transform: ms.Matrix = camera.chunk.transform.matrix

    return transform


def _get_target_crs(camera: ms.Camera) -> ms.CoordinateSystem:
    """Returns the target coordinate system for the camera."""
    if camera.chunk.camera_crs:
        target_crs: ms.CoordinateSystem = camera.chunk.camera_crs
    else:
        target_crs: ms.CoordinateSystem = camera.chunk.crs

    return target_crs


def _get_cartesian_crs(crs: ms.CoordinateSystem) -> ms.CoordinateSystem:
    """Returns a Cartesian coordinate reference system."""
    ecef_crs: ms.CoordinateSystem = crs.geoccs
    if ecef_crs is None:
        ecef_crs: ms.CoordinateSystem = ms.CoordinateSystem("LOCAL")
    return ecef_crs


def _get_antenna_transform(sensor: ms.Sensor) -> ms.Matrix:
    """Returns the GPS antenna transform for a Metashape sensor."""
    location: ms.Vector = sensor.antenna.location

    if location is None:
        location: ms.Vector = sensor.antenna.location_ref
    if location is None:
        location: ms.Vector = ms.Vector([0.0, 0.0, 0.0])

    rotation: ms.Matrix = sensor.antenna.rotation

    if rotation is None:
        rotation: ms.Vector = sensor.antenna.rotation_ref
    if rotation is None:
        rotation: ms.Vector = ms.Vector([0.0, 0.0, 0.0])
    transform: ms.Matrix = (
        ms.Matrix.Diag((1, -1, -1, 1))
        * ms.Matrix.Translation(location)
        * ms.Matrix.Rotation(ms.Utils.ypr2mat(rotation))
    )
    return transform
