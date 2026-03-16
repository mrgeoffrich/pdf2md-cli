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


def normalize_ligatures(text: str) -> str:
    """Replace Unicode ligature codepoints with their multi-character equivalents."""
    ligatures = {
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
        "\ufb05": "st",
        "\ufb06": "st",
    }
    for lig, replacement in ligatures.items():
        text = text.replace(lig, replacement)
    return text


def normalize_bullets(text: str) -> str:
    """Normalize various bullet characters to a consistent markdown list marker."""
    return re.sub(
        r"^[ \t]*[•‣◦●○◆◇▪▸►–—‐‑]\s+",
        "- ",
        text,
        flags=re.MULTILINE,
    )


def merge_orphan_lines(text: str) -> str:
    """Rejoin short lines that are broken by PDF fixed-width layout.

    Joins a line to the next when:
    - The line is shorter than 80 characters
    - The line does not end with sentence-ending punctuation or a colon
    - The line is not a heading, list item, table row, or blank line
    - The next line starts with a lowercase letter
    """
    lines = text.split("\n")
    merged: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (
            i + 1 < len(lines)
            and 0 < len(line) < 80
            and not re.search(r"[.!?:;]\s*$", line)
            and not re.match(r"^\s*(#|[-*+]|\d+\.|>|\|)", line)
            and not line.startswith("---")
            and lines[i + 1]
            and lines[i + 1][0].islower()
        ):
            merged.append(line + " " + lines[i + 1])
            i += 2
        else:
            merged.append(line)
            i += 1
    return "\n".join(merged)


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
    text = normalize_ligatures(text)
    text = normalize_blank_lines(text)
    text = fix_hyphenation(text)
    text = merge_orphan_lines(text)
    text = normalize_bullets(text)
    if max_header_level < 6:
        text = limit_header_depth(text, max_header_level)
    if strip_artifacts:
        text = strip_page_artifacts(text)
    text = normalize_whitespace(text)
    return text
