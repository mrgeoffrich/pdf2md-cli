# Contributing to pdf2md

Thanks for your interest in contributing!

## Getting Started

1. Fork and clone the repo
2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```
3. Create a branch for your change

## Development

Run tests, lint, and format before submitting:

```bash
uv run pytest -v
uv run ruff check .
uv run ruff format .
```

## Style

- `from __future__ import annotations` in every module
- Type hints on all function signatures
- `pathlib.Path` for filesystem ops
- Ruff for lint and format (line-length 88, py310 target)

## Submitting Changes

1. Open a pull request against `main`
2. Describe what your change does and why
3. Make sure CI passes

## Reporting Bugs

Open an issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Python version and OS
