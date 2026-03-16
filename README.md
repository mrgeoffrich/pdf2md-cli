# pdf2md

A CLI tool that converts PDF documents to well-structured Markdown, powered by PyMuPDF4LLM.

## Installation

### From source (pip)

Requires Python 3.10+.

```bash
git clone https://github.com/mrgeoffrich/pdf2md-cli.git
cd pdf2md-cli
pip install .
```

This installs the `pdf2md` command globally. To install in an isolated environment:

```bash
python3 -m venv ~/.pdf2md-venv
~/.pdf2md-venv/bin/pip install .
```

Then either add `~/.pdf2md-venv/bin` to your `PATH` or create an alias:

```bash
alias pdf2md="~/.pdf2md-venv/bin/pdf2md"
```

### Standalone binary (no Python required)

Build a single-file executable with PyInstaller:

```bash
pip install -e ".[dev]"
scripts/build.sh
```

The binary is output to `dist/pdf2md`. Copy it anywhere on your `PATH`:

```bash
cp dist/pdf2md /usr/local/bin/
```

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
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
ruff check .
ruff format .
```
