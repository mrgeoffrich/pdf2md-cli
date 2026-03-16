from __future__ import annotations

import logging
from dataclasses import dataclass

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

    if options.image_path:
        kwargs["image_path"] = options.image_path

    logger.debug("Converting %s with options: %s", path, kwargs)

    try:
        result = pymupdf4llm.to_markdown(path, **kwargs)
    except Exception as exc:
        raise Pdf2mdError(f"Conversion failed: {exc}") from exc

    if not isinstance(result, str):
        raise Pdf2mdError("Unexpected output type from pymupdf4llm")

    return result
