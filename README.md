# pdf2md

Convert PDFs to clean, structured Markdown in one command. Built for the AI age, where feeding documents to LLMs means getting them out of PDF and into a format models can actually work with.

[![CI](https://github.com/mrgeoffrich/pdf2md-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/mrgeoffrich/pdf2md-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

## Installation

### With uv (recommended)

```bash
uv tool install git+https://github.com/mrgeoffrich/pdf2md-cli.git
```

This installs `pdf2md` as an isolated CLI tool. Or run it directly without installing:

```bash
uvx --from git+https://github.com/mrgeoffrich/pdf2md-cli.git pdf2md input.pdf
```

### With pip

Requires Python 3.10+.

```bash
pip install git+https://github.com/mrgeoffrich/pdf2md-cli.git
```

### Standalone binary (no Python required)

Pre-built binaries for Linux, macOS, and Windows are available on the [releases page](https://github.com/mrgeoffrich/pdf2md-cli/releases).

## Usage

```bash
pdf2md input.pdf                          # Output to stdout
pdf2md input.pdf -o output.md             # Output to file
pdf2md input.pdf -p 1-5                   # Convert specific pages
pdf2md input.pdf -p 1,3,7-10             # Convert selected pages
pdf2md input.pdf --images --image-dir img  # Extract images to files
pdf2md input.pdf --embed-images           # Embed images as base64
pdf2md input.pdf --page-breaks            # Insert --- between pages
pdf2md input.pdf --max-header-level 2     # Clamp headings to h2
pdf2md input.pdf --keep-headers-footers   # Preserve running headers/footers
pdf2md input.pdf -v                       # Verbose logging
```

By default, pdf2md strips running headers, footers, and page numbers. Use `--keep-headers-footers` to preserve them.

## Options

| Option | Description |
|---|---|
| `-o`, `--output PATH` | Write to file instead of stdout |
| `-p`, `--pages RANGE` | Page range (e.g. `1-5`, `1,3,7-10`) |
| `--images` / `--no-images` | Extract images to files |
| `--embed-images` | Embed images as base64 in markdown |
| `--image-dir DIR` | Directory for extracted images (default: `./images`) |
| `--image-format {png,jpg}` | Image format (default: `png`) |
| `--dpi N` | DPI for image extraction (default: `150`) |
| `--page-breaks` | Insert `---` between pages |
| `--max-header-level N` | Limit heading depth, 1-6 (default: `6`) |
| `--keep-headers-footers` | Keep running headers/footers (stripped by default) |
| `-v`, `--verbose` | Verbose logging |
| `--version` | Show version |

## Development

```bash
uv sync --extra dev
uv run pytest -v
uv run ruff check .
uv run ruff format .
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
