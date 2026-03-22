from __future__ import annotations

import logging
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pymupdf4llm

from pdf2md.utils import Pdf2mdError

logger = logging.getLogger("pdf2md")


@dataclass
class ConversionOptions:
    """Configuration for PDF to Markdown conversion."""

    pages: list[int] | None = None
    write_images: bool = False
    embed_images: bool = False
    ignore_images: bool = True
    image_path: str = ""
    image_format: str = "png"
    dpi: int = 150
    page_separators: bool = False
    show_progress: bool = False
    strip_headers: bool = True
    strip_footers: bool = True


def convert_pdf(path: str, options: ConversionOptions) -> str:
    """Convert a PDF file to Markdown using PyMuPDF4LLM.

    Args:
        path: Path to the PDF file.
        options: Conversion options controlling extraction behavior.

    Returns:
        The extracted Markdown text.
    """
    kwargs: dict = {
        "write_images": options.write_images,
        "embed_images": options.embed_images,
        "ignore_images": options.ignore_images,
        "image_format": options.image_format,
        "dpi": options.dpi,
        "page_separators": options.page_separators,
        "show_progress": options.show_progress,
        "header": not options.strip_headers,
        "footer": not options.strip_footers,
    }

    if options.pages is not None:
        kwargs["pages"] = options.pages

    # Work around pymupdf4llm replacing spaces with underscores in image
    # paths (utils.md_path sanitizes the save path but the directory is
    # created with the original name, causing a file-not-found error).
    # When the image path contains spaces, write to a temp directory first
    # and relocate the images afterwards.
    real_image_path = options.image_path
    temp_image_dir: str | None = None

    if options.image_path and " " in options.image_path:
        temp_image_dir = tempfile.mkdtemp(prefix="pdf2md_")
        kwargs["image_path"] = temp_image_dir
        logger.debug(
            "Using temp image dir %s (real: %s)", temp_image_dir, real_image_path
        )
    elif options.image_path:
        kwargs["image_path"] = options.image_path

    logger.debug("Converting %s with options: %s", path, kwargs)

    try:
        result = pymupdf4llm.to_markdown(path, **kwargs)
    except Exception as exc:
        if temp_image_dir:
            shutil.rmtree(temp_image_dir, ignore_errors=True)
        raise Pdf2mdError(f"Conversion failed: {exc}") from exc

    if not isinstance(result, str):
        if temp_image_dir:
            shutil.rmtree(temp_image_dir, ignore_errors=True)
        raise Pdf2mdError("Unexpected output type from pymupdf4llm")

    if temp_image_dir:
        result = _relocate_images(temp_image_dir, real_image_path, result)

    return result


def _relocate_images(src_dir: str, dst_dir: str, markdown: str) -> str:
    """Move images from a temp directory to the real destination.

    Also rewrites image references in the markdown text so they point to
    the correct location.
    """
    src = Path(src_dir)
    dst = Path(dst_dir)
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        if item.is_file():
            shutil.move(str(item), str(dst / item.name))

    # pymupdf4llm emits relative posix paths in the markdown — replace the
    # temp dir prefix with the real destination so image links resolve.
    try:
        cwd = Path.cwd()
        src_rel = src.resolve().relative_to(cwd).as_posix()
        dst_rel = dst.resolve().relative_to(cwd).as_posix()
    except ValueError:
        src_rel = src.resolve().as_posix()
        dst_rel = dst.resolve().as_posix()

    markdown = markdown.replace(src_rel, dst_rel)

    shutil.rmtree(src_dir, ignore_errors=True)
    return markdown
