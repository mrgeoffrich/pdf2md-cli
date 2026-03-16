from __future__ import annotations

import re


def normalize_blank_lines(text: str) -> str:
    """Collapse runs of 3+ consecutive newlines down to 2."""
    return re.sub(r"\n{3,}", "\n\n", text)


def fix_hyphenation(text: str) -> str:
    """Rejoin words broken by end-of-line hyphenation.

    Only joins when a lowercase letter precedes the hyphen and a lowercase
    letter follows on the next line, to avoid breaking compound words.
    """
    return re.sub(r"([a-z])-\n([a-z])", r"\1\2", text)


def limit_header_depth(text: str, max_level: int) -> str:
    """Clamp Markdown heading levels to a maximum depth.

    For example, with max_level=3, #### becomes ###.
    """
    if max_level < 1 or max_level > 6:
        return text

    def _clamp(match: re.Match) -> str:
        hashes = match.group(1)
        rest = match.group(2)
        clamped = "#" * min(len(hashes), max_level)
        return f"{clamped}{rest}"

    return re.sub(r"^(#{1,6})([ \t])", _clamp, text, flags=re.MULTILINE)


def strip_page_artifacts(text: str) -> str:
    """Remove common PDF artifacts: standalone page numbers, form feeds."""
    # Remove form feed characters
    text = text.replace("\x0c", "")
    # Remove lines that contain only digits (page numbers)
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    return text


def normalize_whitespace(text: str) -> str:
    """Strip trailing whitespace from lines and ensure single trailing newline."""
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines) + "\n" if lines else ""


def apply_postprocessing(
    text: str,
    *,
    max_header_level: int = 6,
    strip_artifacts: bool = False,
) -> str:
    """Apply the full post-processing pipeline."""
    text = normalize_blank_lines(text)
    text = fix_hyphenation(text)
    if max_header_level < 6:
        text = limit_header_depth(text, max_header_level)
    if strip_artifacts:
        text = strip_page_artifacts(text)
    text = normalize_whitespace(text)
    return text
