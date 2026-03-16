from __future__ import annotations

import pytest

from pdf2md.ocr import check_ocr_available, is_scanned_pdf
from pdf2md.utils import Pdf2mdError


class TestCheckOcrAvailable:
    def test_returns_bool(self):
        result = check_ocr_available()
        assert isinstance(result, bool)


class TestIsScannedPdf:
    def test_text_pdf_not_scanned(self, simple_text_pdf):
        assert is_scanned_pdf(simple_text_pdf) is False


class TestOcrPdfMissingDeps:
    def test_raises_when_deps_missing(self, simple_text_pdf, monkeypatch):
        # Simulate missing pytesseract
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name in ("pytesseract", "pdf2image"):
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        from pdf2md.ocr import ocr_pdf

        with pytest.raises(Pdf2mdError, match="OCR dependencies not installed"):
            ocr_pdf(simple_text_pdf)
