from __future__ import annotations

import sys

import click

from pdf2md import __version__
from pdf2md.converter import ConversionOptions, convert_pdf
from pdf2md.postprocess import apply_postprocessing
from pdf2md.utils import (
    Pdf2mdError,
    ensure_directory,
    parse_page_range,
    setup_logging,
    validate_pdf,
)


@click.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path (default: stdout)",
)
@click.option(
    "-p",
    "--pages",
    default=None,
    help="Page range (e.g. 1-5, 1,3,7-10)",
)
@click.option(
    "--images/--no-images",
    default=False,
    help="Extract images to files",
)
@click.option(
    "--embed-images",
    is_flag=True,
    default=False,
    help="Embed images as base64 in markdown",
)
@click.option(
    "--image-dir",
    default="./images",
    help="Directory for extracted images",
)
@click.option(
    "--image-format",
    type=click.Choice(["png", "jpg"]),
    default="png",
    help="Image format",
)
@click.option(
    "--dpi",
    type=int,
    default=150,
    help="DPI for image extraction",
)
@click.option(
    "--page-breaks",
    is_flag=True,
    default=False,
    help="Insert --- between pages",
)
@click.option(
    "--ocr",
    is_flag=True,
    default=False,
    help="Enable OCR fallback for scanned pages",
)
@click.option(
    "--max-header-level",
    type=click.IntRange(1, 6),
    default=6,
    help="Limit heading depth (1-6)",
)
@click.option(
    "--strip-headers-footers",
    is_flag=True,
    default=False,
    help="Attempt to remove running headers/footers",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Verbose logging",
)
@click.version_option(version=__version__)
def main(
    input_file: str,
    output: str | None,
    pages: str | None,
    images: bool,
    embed_images: bool,
    image_dir: str,
    image_format: str,
    dpi: int,
    page_breaks: bool,
    ocr: bool,
    max_header_level: int,
    strip_headers_footers: bool,
    verbose: bool,
) -> None:
    """Convert a PDF document to well-structured Markdown."""
    setup_logging(verbose)

    # Validate mutual exclusivity
    if images and embed_images:
        raise click.UsageError("--images and --embed-images are mutually exclusive")

    # Parse page range if specified
    page_list: list[int] | None = None
    if pages is not None:
        doc = validate_pdf(input_file)
        page_count = len(doc)
        doc.close()
        page_list = parse_page_range(pages, page_count)

    # Build conversion options
    options = ConversionOptions(
        pages=page_list,
        write_images=images,
        embed_images=embed_images,
        ignore_images=not images and not embed_images,
        image_path=image_dir if images else "",
        image_format=image_format,
        dpi=dpi,
        page_separators=page_breaks,
        show_progress=verbose,
    )

    # Create image directory if needed
    if images:
        ensure_directory(image_dir)

    try:
        # Convert
        result = convert_pdf(input_file, options)

        # OCR fallback
        if ocr and (not result or not result.strip()):
            from pdf2md.ocr import check_ocr_available, ocr_pdf

            if check_ocr_available():
                result = ocr_pdf(input_file, pages=page_list, dpi=dpi)
            else:
                click.echo(
                    "Warning: OCR requested but dependencies "
                    "not available. "
                    "Install with: pip install pdf2md[ocr]",
                    err=True,
                )

        # Post-process
        result = apply_postprocessing(
            result,
            max_header_level=max_header_level,
            strip_artifacts=strip_headers_footers,
        )

        # Output
        if output:
            from pathlib import Path

            Path(output).parent.mkdir(parents=True, exist_ok=True)
            Path(output).write_text(result, encoding="utf-8")
            click.echo(f"Written to {output}", err=True)
        else:
            click.echo(result, nl=False)

    except Pdf2mdError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
