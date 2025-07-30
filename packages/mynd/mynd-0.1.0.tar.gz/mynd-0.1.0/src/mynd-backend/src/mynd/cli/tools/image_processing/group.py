"""CLI group for invoking image processing tasks from the command-line."""

from pathlib import Path

import click
import tqdm

from mynd.image import Image, read_image, write_image, process_image_linear
from mynd.utils.filesystem import list_directory
from mynd.utils.log import logger


@click.group()
def image_processing_group() -> None:
    """Group for image processing commands."""
    pass


@image_processing_group.command()
@click.option("--input", "input_directory", type=Path, required=True)
@click.option("--output", "output_directory", type=Path, required=True)
@click.option("--brightness", type=float, required=True)
@click.option("--contrast", type=float, required=True)
@click.option("--pattern", type=str, default="*")
def process_images_linear(
    input_directory: Path,
    output_directory: Path,
    brightness: float,
    contrast: float,
    pattern: str,
) -> None:
    """Processes images with linear brightness and contrast adjustment, and writes the processed images to file."""

    assert input_directory.exists(), f"directory does not exist: {input_directory}"
    assert input_directory.is_dir(), f"path is not a directory: {input_directory}"

    assert (
        output_directory.parent.exists()
    ), f"directory does not exist: {output_directory.parent}"
    assert (
        output_directory.parent.is_dir()
    ), f"path is not a directory: {output_directory.parent}"
    
    assert input_directory != output_directory, "input and output directories cannot be the same"

    assert brightness > 0.0, "brightness scale must be positive"
    assert contrast > 0.0, "brightness scale must be positive"

    output_directory.mkdir(exist_ok=True)

    files: list[Path] = list_directory(input_directory, pattern=pattern)

    logger.info("")
    logger.info("Image processing - linear brightness / contrast adjustment:")
    logger.info(f" - Input:         {input_directory.name}")
    logger.info(f" - Output:        {output_directory.name}")
    logger.info(f" - Brightness:    {brightness}")
    logger.info(f" - Contrast:      {contrast}")
    logger.info("")

    for path in tqdm.tqdm(files, desc="Processing images..."):
        unprocessed_image: Image = read_image(path)
        processed_image: Image = process_image_linear(
            unprocessed_image, brightness=brightness, contrast=contrast
        )

        result: Path | str = write_image(
            image=processed_image, uri=output_directory / path.name
        )

        # If the write result is an error, we log and raise
        if isinstance(result, str):
            logger.info(result)
            raise ValueError(result)
