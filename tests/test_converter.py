from __future__ import annotations

from pathlib import Path

from pdf2md.converter import ConversionOptions, convert_pdf


class TestConvertPdf:
    def test_simple_text_has_headings(self, simple_text_pdf):
        result = convert_pdf(simple_text_pdf, ConversionOptions())
        assert "Main Title" in result
        assert "Section One" in result
        assert "Section Two" in result

    def test_simple_text_has_formatting(self, simple_text_pdf):
        result = convert_pdf(simple_text_pdf, ConversionOptions())
        assert "**bold text**" in result
        assert "italic text" in result

    def test_with_tables_has_content(self, with_tables_pdf):
        result = convert_pdf(with_tables_pdf, ConversionOptions())
        assert "Table Document" in result
        assert "Alice" in result
        assert "Bob" in result

    def test_with_lists_has_unordered(self, with_lists_pdf):
        result = convert_pdf(with_lists_pdf, ConversionOptions())
        assert "First item" in result
        assert "Second item" in result

    def test_with_lists_has_ordered(self, with_lists_pdf):
        result = convert_pdf(with_lists_pdf, ConversionOptions())
        assert "Step one" in result
        assert "Step two" in result

    def test_page_selection(self, multi_page_pdf):
        result = convert_pdf(multi_page_pdf, ConversionOptions(pages=[0]))
        # First page should have content, but not all sections
        assert "Multi-Page Document" in result or "Section 1" in result

    def test_page_separators(self, multi_page_pdf):
        result = convert_pdf(multi_page_pdf, ConversionOptions(page_separators=True))
        assert "---" in result

    def test_ignore_images_default(self, simple_text_pdf):
        result = convert_pdf(simple_text_pdf, ConversionOptions())
        # With ignore_images=True (default), no image references
        assert "![" not in result

    def test_returns_string(self, simple_text_pdf):
        result = convert_pdf(simple_text_pdf, ConversionOptions())
        assert isinstance(result, str)
        assert len(result) > 0


class TestImageDirWithSpaces:
    def test_image_dir_with_spaces(self, with_image_pdf, tmp_path):
        """Regression test: spaces in image-dir path should not cause errors."""
        image_dir = str(tmp_path / "dir with spaces" / "images here")
        options = ConversionOptions(
            write_images=True,
            ignore_images=False,
            image_path=image_dir,
        )
        result = convert_pdf(with_image_pdf, options)
        # Images should be written to the directory with spaces
        written = list(Path(image_dir).glob("*.png"))
        assert len(written) > 0, "No images written to directory with spaces"
        # Markdown should reference the real path, not a temp path
        assert "pdf2md_" not in result

    def test_image_dir_without_spaces(self, with_image_pdf, tmp_path):
        """Image extraction works normally for paths without spaces."""
        image_dir = str(tmp_path / "normal_images")
        options = ConversionOptions(
            write_images=True,
            ignore_images=False,
            image_path=image_dir,
        )
        convert_pdf(with_image_pdf, options)
        written = list(Path(image_dir).glob("*.png"))
        assert len(written) > 0, "No images written to directory"
