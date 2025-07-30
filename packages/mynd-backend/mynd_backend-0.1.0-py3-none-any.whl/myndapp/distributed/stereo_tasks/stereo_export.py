"""Module for tasks for exporting stereo data."""

from pathlib import Path
from typing import ClassVar, TypeAlias

import numpy as np

from pydantic import BaseModel, Field

import mynd.schemas as schemas
import mynd.geometry.stereo as stereo

from mynd.image import Image, read_image, write_image
from mynd.utils.containers import Pair
from mynd.utils.log import logger

from myndapp.distributed.worker import celery_app


ImageFilePair: TypeAlias = Pair[Path]


class StereoExportDirectories(BaseModel):
    """Class representing stereo export directories."""

    images: Path
    ranges: Path
    normals: Path


class StereoExportTask(BaseModel):
    """Class representing data for a stereo export task."""

    Directories: ClassVar[TypeAlias] = StereoExportDirectories

    directories: Directories = Field(default_factory=StereoExportDirectories)


@celery_app.task
def export_stereo_rectified_images(
    directory: Path,
    stereo_rig: schemas.StereoRigWithMapsSchema,
    image_file_pairs: list[ImageFilePair],
) -> None:
    """Exports stereo rectified images to a directory."""

    assert directory.exists(), f"directory does not exist: {directory}"

    pixel_map_pair: Pair[stereo.PixelMap] = Pair(
        first=stereo.PixelMap(stereo_rig.pixel_maps.master.to_array()),
        second=stereo.PixelMap(stereo_rig.pixel_maps.slave.to_array()),
    )

    for image_file_pair in image_file_pairs:
        image_pair: Pair[Image] = Pair(
            first=read_image(image_file_pair.first),
            second=read_image(image_file_pair.second),
        )

        rectified_image_pair: Pair[Image] = stereo.rectify_image_pair(
            images=image_pair, pixel_maps=pixel_map_pair
        )

        write_image(
            rectified_image_pair.first,
            directory / f"{image_file_pair.first.stem}.tiff",
        )
        write_image(
            rectified_image_pair.second,
            directory / f"{image_file_pair.second.stem}.tiff",
        )


@celery_app.task
def export_stereo_rectified_masks(
    directory: Path,
    stereo_rig: schemas.StereoRigWithMapsSchema,
    camera_pairs: list[schemas.StereoRigSchema.CameraPair],
) -> None:
    """Exports image masks rectified by a calibrated stereo rig."""
    for camera_pair in camera_pairs:
        _export_mask(
            stereo_rig.pixel_maps.master, directory / f"{camera_pair.master.label}.tiff"
        )
        _export_mask(
            stereo_rig.pixel_maps.slave, directory / f"{camera_pair.slave.label}.tiff"
        )


def _export_mask(pixel_map: schemas.PixelMapSchema, path: Path) -> None:
    """Export a camera mask to the directory."""
    mask: Image = _undistort_image_mask(pixel_map)
    result: Path | str = write_image(mask, path)
    if isinstance(result, str):
        logger.error(result)
        raise ValueError(result)


def _undistort_image_mask(pixel_map: schemas.PixelMapSchema) -> Image:
    """Undistorts an image mask."""
    INIT_VALUE: int = 255

    init_values: np.ndarray = np.full(
        shape=(pixel_map.height, pixel_map.width),
        fill_value=INIT_VALUE,
        dtype=np.uint8,
    )

    distorted_mask: Image = Image.from_array(
        data=init_values,
        pixel_format=Image.Format.GRAY,
    )

    undistorted_mask: Image = stereo.remap_image_pixels(
        image=distorted_mask,
        pixel_map=pixel_map,
    )

    values: np.ndarray = undistorted_mask.to_array()
    values[values > 0] = INIT_VALUE

    return Image.from_array(values, pixel_format=Image.Format.GRAY)


@celery_app.task
def export_stereo_range_maps(
    directories: StereoExportTask.Directories,
    stereo_rig: schemas.StereoRigWithMapsSchema,
    image_file_pairs: list[ImageFilePair],
    matcher_file: Path,
) -> None:
    """Generates stereo range maps by matching a pair of stereo images."""

    assert (
        directories.ranges.exists()
    ), f"directory does not exist: {directories.ranges}"
    assert matcher_file.exists(), f"matcher file does not exist: {matcher_file}"

    stereo_matcher: stereo.StereoMatcher = stereo.create_hitnet_matcher(matcher_file)

    pixel_map_pair: Pair[stereo.PixelMap] = Pair(
        first=stereo.PixelMap(stereo_rig.pixel_maps.master.to_array()),
        second=stereo.PixelMap(stereo_rig.pixel_maps.slave.to_array()),
    )

    for image_file_pair in image_file_pairs:
        image_pair: Pair[Image] = Pair(
            first=read_image(image_file_pair.first),
            second=read_image(image_file_pair.second),
        )

        rectified_image_pair: Pair[Image] = stereo.rectify_image_pair(
            images=image_pair, pixel_maps=pixel_map_pair
        )

        stereo_geometry: stereo.StereoGeometry = stereo.compute_stereo_geometry(
            sensors_rectified=stereo_rig.sensors_rectified,
            images_rectified=rectified_image_pair,
            matcher=stereo_matcher,
        )

        # TODO: Add callback to export range maps / normal maps
        write_image(
            stereo_geometry.range_maps.first,
            directories.ranges / f"{image_file_pair.first.stem}.tiff",
        )
        write_image(
            stereo_geometry.range_maps.second,
            directories.ranges / f"{image_file_pair.second.stem}.tiff",
        )


@celery_app.task
def export_stereo_geometry(
    directories: StereoExportTask.Directories,
    stereo_rig: schemas.StereoRigWithMapsSchema,
    image_file_pairs: list[ImageFilePair],
    matcher_file: Path,
) -> None:
    """Export stereo range and normal maps."""

    assert (
        directories.ranges.exists()
    ), f"directory does not exist: {directories.ranges}"
    assert (
        directories.normals.exists()
    ), f"directory does not exist: {directories.normals}"
    assert matcher_file.exists(), f"matcher file does not exist: {matcher_file}"

    stereo_matcher: stereo.StereoMatcher = stereo.create_hitnet_matcher(matcher_file)

    pixel_map_pair: Pair[stereo.PixelMap] = Pair(
        first=stereo.PixelMap(stereo_rig.pixel_maps.master.to_array()),
        second=stereo.PixelMap(stereo_rig.pixel_maps.slave.to_array()),
    )

    for image_file_pair in image_file_pairs:
        image_pair: Pair[Image] = Pair(
            first=read_image(image_file_pair.first),
            second=read_image(image_file_pair.second),
        )

        rectified_image_pair: Pair[Image] = stereo.rectify_image_pair(
            images=image_pair, pixel_maps=pixel_map_pair
        )

        stereo_geometry: stereo.StereoGeometry = stereo.compute_stereo_geometry(
            sensors_rectified=stereo_rig.sensors_rectified,
            images_rectified=rectified_image_pair,
            matcher=stereo_matcher,
        )

        # Write range maps to file
        write_image(
            stereo_geometry.range_maps.first,
            directories.ranges / f"{image_file_pair.first.stem}.tiff",
        )
        write_image(
            stereo_geometry.range_maps.second,
            directories.ranges / f"{image_file_pair.second.stem}.tiff",
        )

        # Write normal maps to file
        write_image(
            stereo_geometry.normal_maps.first,
            directories.normals / f"{image_file_pair.first.stem}.tiff",
        )
        write_image(
            stereo_geometry.normal_maps.second,
            directories.normals / f"{image_file_pair.second.stem}.tiff",
        )
