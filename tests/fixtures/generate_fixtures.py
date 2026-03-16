"""Generate test PDF fixtures using PyMuPDF's Story API.

Run this module directly to regenerate fixtures:
    python -m tests.fixtures.generate_fixtures
"""

from __future__ import annotations

from pathlib import Path

import pymupdf

FIXTURES_DIR = Path(__file__).parent


def _write_story_pdf(html: str, output: Path, css: str = "") -> None:
    """Render HTML content to a PDF using PyMuPDF Story API."""
    story = pymupdf.Story(html, user_css=css)
    writer = pymupdf.DocumentWriter(str(output))
    mediabox = pymupdf.paper_rect("letter")
    content_rect = mediabox + (72, 72, -72, -72)

    more = True
    while more:
        dev = writer.begin_page(mediabox)
        more, _ = story.place(content_rect)
        story.draw(dev)
        writer.end_page()

    writer.close()


def generate_simple_text() -> None:
    """Generate a simple PDF with headings and paragraphs."""
    html = """
    <h1>Main Title</h1>
    <p>This is the first paragraph under the main title. It contains some
    body text to test basic paragraph extraction.</p>
    <h2>Section One</h2>
    <p>Content under section one. This paragraph has multiple sentences
    to ensure proper text flow extraction.</p>
    <h2>Section Two</h2>
    <p>Content under section two with <b>bold text</b> and <i>italic text</i>
    for testing inline formatting.</p>
    """
    _write_story_pdf(html, FIXTURES_DIR / "simple_text.pdf")


def generate_with_tables() -> None:
    """Generate a PDF containing a table."""
    html = """
    <h1>Table Document</h1>
    <p>This document contains a table.</p>
    <table>
        <tr><th>Name</th><th>Age</th><th>City</th></tr>
        <tr><td>Alice</td><td>30</td><td>New York</td></tr>
        <tr><td>Bob</td><td>25</td><td>London</td></tr>
        <tr><td>Charlie</td><td>35</td><td>Tokyo</td></tr>
    </table>
    <p>Text after the table.</p>
    """
    _write_story_pdf(html, FIXTURES_DIR / "with_tables.pdf")


def generate_multi_page() -> None:
    """Generate a multi-page PDF."""
    paragraphs = []
    for i in range(1, 6):
        paragraphs.append(f"<h2>Section {i}</h2>")
        for j in range(5):
            paragraphs.append(
                f"<p>This is paragraph {j + 1} of section {i}. "
                "It contains enough text to help fill the page and push content "
                "across multiple pages for testing page range selection and "
                "page break insertion functionality.</p>"
            )
    html = f"<h1>Multi-Page Document</h1>{''.join(paragraphs)}"
    _write_story_pdf(html, FIXTURES_DIR / "multi_page.pdf")


def generate_with_lists() -> None:
    """Generate a PDF with ordered and unordered lists."""
    html = """
    <h1>List Document</h1>
    <h2>Unordered List</h2>
    <ul>
        <li>First item</li>
        <li>Second item</li>
        <li>Third item</li>
    </ul>
    <h2>Ordered List</h2>
    <ol>
        <li>Step one</li>
        <li>Step two</li>
        <li>Step three</li>
    </ol>
    """
    _write_story_pdf(html, FIXTURES_DIR / "with_lists.pdf")


def generate_all() -> None:
    """Generate all test PDF fixtures."""
    generate_simple_text()
    generate_with_tables()
    generate_multi_page()
    generate_with_lists()


if __name__ == "__main__":
    generate_all()
    print(f"Fixtures generated in {FIXTURES_DIR}")
