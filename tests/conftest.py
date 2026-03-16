from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def generate_test_pdfs():
    """Generate test PDF fixtures before the test session."""
    from tests.fixtures.generate_fixtures import generate_all

    generate_all()


@pytest.fixture
def simple_text_pdf() -> str:
    return str(FIXTURES_DIR / "simple_text.pdf")


@pytest.fixture
def with_tables_pdf() -> str:
    return str(FIXTURES_DIR / "with_tables.pdf")


@pytest.fixture
def multi_page_pdf() -> str:
    return str(FIXTURES_DIR / "multi_page.pdf")


@pytest.fixture
def with_lists_pdf() -> str:
    return str(FIXTURES_DIR / "with_lists.pdf")


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()
