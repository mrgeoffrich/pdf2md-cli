# pdf2md

A CLI tool that converts PDF documents to well-structured Markdown, distributed as a standalone binary.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
pdf2md input.pdf                          # Output to stdout
pdf2md input.pdf -o output.md             # Output to file
pdf2md input.pdf -p 1-5                   # Convert specific pages
pdf2md input.pdf --images --image-dir img  # Extract images
pdf2md input.pdf --page-breaks            # Insert --- between pages
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
ruff check .
```
