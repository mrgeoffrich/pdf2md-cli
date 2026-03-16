# pdf2md-cli

PDF-to-Markdown CLI using PyMuPDF4LLM. Standalone binary via PyInstaller.

## Commands

```bash
source .venv/bin/activate
pytest -v              # run tests (67 tests)
ruff check .           # lint
ruff format .          # format
scripts/build.sh       # pyinstaller binary build
```

## Structure

- `pdf2md/cli.py` — click command, entry point
- `pdf2md/converter.py` — PyMuPDF4LLM wrapper, `ConversionOptions` dataclass
- `pdf2md/postprocess.py` — pure string transforms (blank lines, hyphenation, headers, artifacts)
- `pdf2md/utils.py` — PDF validation, page range parsing, logging
- `tests/fixtures/generate_fixtures.py` — creates test PDFs at runtime via PyMuPDF Story API (no PDFs in git)

## Style

- `from __future__ import annotations` in every module
- Type hints on all function signatures (`def foo(path: str) -> list[int]:`)
- Use `X | None` union syntax, not `Optional[X]`
- Dataclasses for structured config (see `ConversionOptions`)
- `pathlib.Path` for filesystem ops, not `os.path`
- Ruff for lint+format (line-length 88, py310 target)
- `pyproject.toml` only (hatchling build backend, no setup.py)

## Testing

- Structural assertions for converter tests (not exact match — pymupdf4llm output varies)
- Exact match for postprocess tests (we control the input)
- Test PDFs generated at runtime via PyMuPDF Story API (no binaries in git)
- Click `CliRunner` for CLI integration tests
