from __future__ import annotations

import click
import pytest

from pdf2md.utils import parse_page_range, validate_pdf


class TestParsePageRange:
    def test_single_page(self):
        assert parse_page_range("1", 10) == [0]

    def test_single_page_last(self):
        assert parse_page_range("10", 10) == [9]

    def test_range(self):
        assert parse_page_range("1-5", 10) == [0, 1, 2, 3, 4]

    def test_comma_separated(self):
        assert parse_page_range("1,3,5", 10) == [0, 2, 4]

    def test_mixed_range_and_single(self):
        assert parse_page_range("1,3,7-10", 10) == [0, 2, 6, 7, 8, 9]

    def test_overlapping_ranges_deduplicated(self):
        assert parse_page_range("1-5,3-7", 10) == [0, 1, 2, 3, 4, 5, 6]

    def test_single_page_range(self):
        assert parse_page_range("3-3", 10) == [2]

    def test_whitespace_handling(self):
        assert parse_page_range(" 1 , 3 ", 10) == [0, 2]

    def test_reversed_range_raises(self):
        with pytest.raises(click.BadParameter, match="start > end"):
            parse_page_range("5-3", 10)

    def test_zero_page_raises(self):
        with pytest.raises(click.BadParameter, match=">= 1"):
            parse_page_range("0", 10)

    def test_page_out_of_range(self):
        with pytest.raises(click.BadParameter, match="out of range"):
            parse_page_range("11", 10)

    def test_range_end_out_of_range(self):
        with pytest.raises(click.BadParameter, match="out of range"):
            parse_page_range("5-11", 10)

    def test_invalid_format(self):
        with pytest.raises(click.BadParameter):
            parse_page_range("abc", 10)

    def test_empty_string_raises(self):
        with pytest.raises(click.BadParameter, match="cannot be empty"):
            parse_page_range("", 10)

    def test_empty_part_raises(self):
        with pytest.raises(click.BadParameter):
            parse_page_range("1,,3", 10)


class TestValidatePdf:
    def test_valid_pdf(self, simple_text_pdf):
        doc = validate_pdf(simple_text_pdf)
        assert len(doc) > 0
        doc.close()

    def test_nonexistent_file(self):
        with pytest.raises(click.BadParameter, match="File not found"):
            validate_pdf("/nonexistent/path.pdf")

    def test_non_pdf_file(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a pdf")
        with pytest.raises(click.BadParameter):
            validate_pdf(str(txt_file))
