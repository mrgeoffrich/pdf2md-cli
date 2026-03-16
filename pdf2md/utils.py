from __future__ import annotations

import logging
import os
from pathlib import Path

import click
import pymupdf


class Pdf2mdError(Exception):
    """Base exception for pdf2md."""


def setup_logging(verbose: bool) -> logging.Logger:
    """Configure and return the pdf2md logger."""
    logger = logging.getLogger("pdf2md")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    return logger


def validate_pdf(path: str) -> pymupdf.Document:
    """Open and validate a PDF file, returning the Document."""
    if not os.path.exists(path):
        raise click.BadParameter(f"File not found: {path}")

    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        raise click.BadParameter(f"Cannot open file as PDF: {path}") from exc

    if not doc.is_pdf:
        doc.close()
        raise click.BadParameter(f"Not a valid PDF file: {path}")

    logger = logging.getLogger("pdf2md")
    logger.debug("Opened %s: %d pages", path, len(doc))
    return doc


def parse_page_range(spec: str, page_count: int) -> list[int]:
    """Parse a page range string into 0-based page indices.

    Accepts formats like "1", "1-5", "1,3,7-10".
    Pages are 1-based in the input, converted to 0-based output.
    """
    if not spec or not spec.strip():
        raise click.BadParameter("Page range cannot be empty")

    pages: set[int] = set()

    for part in spec.split(","):
        part = part.strip()
        if not part:
            raise click.BadParameter(f"Invalid page range: {spec}")

        if "-" in part:
            bounds = part.split("-", 1)
            try:
                start = int(bounds[0])
                end = int(bounds[1])
            except ValueError:
                raise click.BadParameter(f"Invalid page range: {part}")

            if start > end:
                raise click.BadParameter(f"Invalid page range: {part} (start > end)")
            if start < 1:
                raise click.BadParameter(f"Page number must be >= 1, got {start}")
            if end > page_count:
                raise click.BadParameter(
                    f"Page {end} out of range (document has {page_count} pages)"
                )
            pages.update(range(start - 1, end))
        else:
            try:
                page_num = int(part)
            except ValueError:
                raise click.BadParameter(f"Invalid page number: {part}")

            if page_num < 1:
                raise click.BadParameter(f"Page number must be >= 1, got {page_num}")
            if page_num > page_count:
                raise click.BadParameter(
                    f"Page {page_num} out of range (document has {page_count} pages)"
                )
            pages.add(page_num - 1)

    return sorted(pages)


def ensure_directory(path: str) -> None:
    """Create a directory and parents if they don't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)
