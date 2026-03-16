from __future__ import annotations

import logging

import pymupdf

from pdf2md.utils import Pdf2mdError

logger = logging.getLogger("pdf2md")


def check_ocr_available() -> bool:
    """Check if OCR dependencies (pytesseract, pdf2image) are installed."""
    try:
        import pdf2image  # noqa: F401
        import pytesseract  # noqa: F401

        return True
    except ImportError:
        return False


def ocr_pdf(
    path: str,
    pages: list[int] | None = None,
    dpi: int = 300,
    language: str = "eng",
) -> str:
    """Convert a scanned PDF to text using OCR.

    Requires pytesseract and pdf2image to be installed:
        pip install pdf2md[ocr]
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        raise Pdf2mdError(
            "OCR dependencies not installed. Install with: pip install pdf2md[ocr]"
        )

    logger.debug("Running OCR on %s (dpi=%d, lang=%s)", path, dpi, language)

    all_images = convert_from_path(path, dpi=dpi)

    if pages is not None:
        images = [all_images[i] for i in pages if i < len(all_images)]
    else:
        images = all_images

    results = []
    for i, image in enumerate(images):
        logger.debug("OCR processing page %d", i + 1)
        text = pytesseract.image_to_string(image, lang=language)
        results.append(text)

    return "\n\n---\n\n".join(results)


def is_scanned_pdf(path: str, threshold: float = 10.0) -> bool:
    """Heuristic check: is this PDF mostly scanned images?

    Returns True if the average characters per page is below the threshold.
    """
    doc = pymupdf.open(path)
    if len(doc) == 0:
        doc.close()
        return False

    total_chars = sum(len(page.get_text()) for page in doc)
    avg_chars = total_chars / len(doc)
    doc.close()

    logger.debug("Average chars per page: %.1f (threshold: %.1f)", avg_chars, threshold)
    return avg_chars < threshold
