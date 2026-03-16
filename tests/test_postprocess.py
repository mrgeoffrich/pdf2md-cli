from __future__ import annotations

from pdf2md.postprocess import (
    apply_postprocessing,
    fix_hyphenation,
    limit_header_depth,
    normalize_blank_lines,
    normalize_whitespace,
    strip_page_artifacts,
)


class TestNormalizeBlankLines:
    def test_collapses_multiple_blank_lines(self):
        assert normalize_blank_lines("a\n\n\n\n\nb") == "a\n\nb"

    def test_preserves_double_newline(self):
        assert normalize_blank_lines("a\n\nb") == "a\n\nb"

    def test_preserves_single_newline(self):
        assert normalize_blank_lines("a\nb") == "a\nb"

    def test_handles_empty_string(self):
        assert normalize_blank_lines("") == ""


class TestFixHyphenation:
    def test_joins_hyphenated_word(self):
        assert fix_hyphenation("docu-\nment") == "document"

    def test_preserves_compound_word_at_line_end(self):
        # Uppercase after hyphen: don't join
        assert fix_hyphenation("self-\nAware") == "self-\nAware"

    def test_preserves_hyphen_after_uppercase(self):
        # Uppercase before hyphen: don't join
        assert fix_hyphenation("A-\nword") == "A-\nword"

    def test_no_hyphen_no_change(self):
        assert fix_hyphenation("hello\nworld") == "hello\nworld"


class TestLimitHeaderDepth:
    def test_clamps_deep_header(self):
        assert limit_header_depth("#### Deep heading", 3) == "### Deep heading"

    def test_preserves_shallow_header(self):
        assert limit_header_depth("## Shallow", 3) == "## Shallow"

    def test_clamps_to_h1(self):
        assert limit_header_depth("### Header", 1) == "# Header"

    def test_h6_unchanged_at_max_6(self):
        assert limit_header_depth("###### H6", 6) == "###### H6"

    def test_multiple_headers(self):
        text = "# H1\n## H2\n### H3\n#### H4"
        expected = "# H1\n## H2\n## H3\n## H4"
        assert limit_header_depth(text, 2) == expected

    def test_does_not_affect_inline_hashes(self):
        assert limit_header_depth("code with # comment", 1) == "code with # comment"


class TestStripPageArtifacts:
    def test_removes_standalone_page_number(self):
        assert strip_page_artifacts("text\n42\nmore") == "text\n\nmore"

    def test_preserves_numbers_in_text(self):
        assert strip_page_artifacts("page 42 here") == "page 42 here"

    def test_removes_form_feed(self):
        assert strip_page_artifacts("before\x0cafter") == "beforeafter"

    def test_removes_page_number_with_trailing_space(self):
        assert strip_page_artifacts("text\n42  \nmore") == "text\n\nmore"


class TestNormalizeWhitespace:
    def test_strips_trailing_spaces(self):
        assert normalize_whitespace("hello   \nworld  ") == "hello\nworld\n"

    def test_ensures_trailing_newline(self):
        assert normalize_whitespace("hello") == "hello\n"

    def test_empty_string(self):
        assert normalize_whitespace("") == ""

    def test_preserves_content(self):
        assert normalize_whitespace("line1\nline2\n") == "line1\nline2\n"


class TestApplyPostprocessing:
    def test_full_pipeline(self):
        text = "# Title\n\n\n\n\nSome docu-\nment text.\n42\n"
        result = apply_postprocessing(text, max_header_level=6, strip_artifacts=True)
        assert "document text" in result
        assert "\n\n\n" not in result

    def test_header_clamping_disabled_at_6(self):
        text = "###### Deep\n"
        result = apply_postprocessing(text, max_header_level=6)
        assert result.startswith("###### Deep")

    def test_header_clamping_enabled(self):
        text = "#### Deep\n"
        result = apply_postprocessing(text, max_header_level=2)
        assert result.startswith("## Deep")

    def test_artifact_stripping_disabled_by_default(self):
        text = "text\n42\nmore\n"
        result = apply_postprocessing(text)
        assert "42" in result
