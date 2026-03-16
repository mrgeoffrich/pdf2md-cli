from __future__ import annotations

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
