# pdf2md — Technical Specification

## Overview

A CLI tool that converts PDF documents to well-structured Markdown, distributed as a standalone binary for easy use across machines without requiring a Python environment.

## Problem Statement

Converting PDFs to Markdown is a common need for documentation pipelines, LLM/RAG ingestion, and content migration. Existing solutions either require a full Python stack on the target machine or produce low-quality output that loses document structure (headings, tables, emphasis, lists).

The goal is a tool that produces high-quality Markdown output comparable to PyMuPDF4LLM while being distributable as a single binary.

## Key Technical Decisions

### Extraction Engine: PyMuPDF4LLM

PyMuPDF4LLM was selected as the core extraction library after evaluating several alternatives.

**Why PyMuPDF4LLM over alternatives:**

- **vs pdfplumber:** PyMuPDF4LLM provides heading detection via font size analysis out of the box. pdfplumber gives raw character-level metadata but requires custom heuristics for structure inference — essentially reimplementing what PyMuPDF4LLM already does.
- **vs Go-based solutions (go-fitz, PDFtoMD):** The Go ecosystem lacks libraries with intelligent structure detection. The best Go approach (go-fitz HTML → html-to-markdown) produces noticeably lower quality output and go-fitz carries an AGPL license.
- **vs marker-pdf:** Marker uses deep learning models for layout detection, which produces excellent results but adds significant binary size and startup time. Overkill for most documents.

**What PyMuPDF4LLM handles well:**

- Header detection via font size popularity analysis (most common size = body text, larger = headers)
- Table detection and GitHub-flavoured Markdown table output
- Multi-column layout support with correct reading order
- Bold, italic, monospace, and code block detection
- Ordered and unordered list formatting
- Image extraction (saved to files or embedded as base64)
- Page header/footer filtering (when used with PyMuPDF Layout)

**Known limitations to be aware of:**

- Tables without visible vertical borders may be treated as plain text
- Code block language specifiers (e.g. `python`) are not preserved
- Heavily designed PDFs (marketing materials, magazines) may not convert cleanly
- Scanned/image-only PDFs require OCR as a separate step

### Distribution: PyInstaller

The tool will be packaged as a standalone binary using PyInstaller to eliminate the need for Python on target machines.

**Why PyInstaller over alternatives:**

- **vs Nuitka:** Nuitka compiles Python to C and can produce smaller, faster binaries. However, it has a longer, more complex build process and occasional compatibility issues with C-extension-heavy libraries like PyMuPDF. PyInstaller is more battle-tested for this use case.
- **vs Docker:** Docker solves the distribution problem but requires Docker on the target machine and adds overhead for a simple CLI tool. Not appropriate for quick ad-hoc use.
- **vs shiv/zipapp:** These still require a compatible Python interpreter on the target machine, which defeats the purpose.

**PyInstaller considerations:**

- Binary size will be in the range of 30-60 MB due to bundled Python interpreter and PyMuPDF native libraries
- Build must happen on each target platform (Linux binary built on Linux, macOS on macOS, etc.) — CI/CD can automate this
- `--onefile` mode bundles everything into a single executable (slower startup due to temp extraction) vs `--onedir` mode (faster startup, but a folder to distribute)
- PyMuPDF's native `.so`/`.dylib` dependencies need to be correctly detected — may require explicit `--hidden-import` or `--collect-all` flags

### CLI Framework: click

`click` was chosen over `argparse` for the CLI interface.

**Rationale:** click provides a cleaner API for building composable CLI tools, better help text formatting, automatic environment variable support, and easier testing via `CliRunner`. For a tool that may grow subcommands over time (e.g. `pdf2md convert`, `pdf2md info`, `pdf2md batch`), click's decorator-based approach scales better than argparse.

## Architecture

### Component Overview

```
┌─────────────────────────────────────────┐
│                CLI Layer                 │
│         (click commands + args)          │
├─────────────────────────────────────────┤
│            Conversion Engine             │
│    (PyMuPDF4LLM wrapper + options)       │
├─────────────────────────────────────────┤
│           Post-Processing                │
│  (cleanup, header/footer strip, etc.)    │
├─────────────────────────────────────────┤
│              Output Layer                │
│   (file write, stdout, page chunking)    │
└─────────────────────────────────────────┘
```

### Module Structure

```
pdf2md/
├── __init__.py
├── __main__.py          # Entry point for `python -m pdf2md`
├── cli.py               # click command definitions
├── converter.py         # Core conversion logic wrapping PyMuPDF4LLM
├── postprocess.py       # Markdown cleanup and normalisation
├── ocr.py               # Optional OCR fallback for scanned pages
└── utils.py             # Shared helpers (logging, file handling)
```

### Conversion Pipeline

1. **Input validation** — verify file exists, is a valid PDF, check page count
2. **Page selection** — apply `--pages` range filter if specified
3. **Extraction** — call `pymupdf4llm.to_markdown()` with configured options
4. **Post-processing** — clean up common artefacts:
   - Normalise excessive blank lines
   - Strip repeated headers/footers (if detected across pages)
   - Fix broken words from line-wrap hyphenation
   - Optionally collapse single-line paragraphs that were split by page boundaries
5. **Image handling** — based on flags, either save images to a directory, embed as base64, or skip entirely
6. **Output** — write to file or stdout

## CLI Interface

### Primary Command

```
pdf2md <input.pdf> [options]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Output file path | stdout |
| `-p, --pages` | Page range (e.g. `1-5`, `1,3,7-10`) | all pages |
| `--images / --no-images` | Extract images to files | `--no-images` |
| `--embed-images` | Embed images as base64 in markdown | off |
| `--image-dir` | Directory for extracted images | `./images` |
| `--image-format` | Image format: png, jpg | png |
| `--dpi` | DPI for image extraction | 150 |
| `--page-breaks` | Insert `---` between pages | off |
| `--ocr` | Enable OCR fallback for scanned pages | off |
| `--max-header-level` | Limit heading depth (1-6) | 6 |
| `--strip-headers-footers` | Attempt to remove running headers/footers | off |
| `-v, --verbose` | Verbose logging | off |

### Planned Subcommands (Future)

- `pdf2md info <input.pdf>` — show PDF metadata, page count, detected structure summary
- `pdf2md batch <directory>` — convert all PDFs in a directory

## Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| pymupdf4llm | Core PDF→Markdown extraction | latest |
| pymupdf | Underlying PDF engine (installed with pymupdf4llm) | latest |
| click | CLI framework | >=8.0 |
| pytesseract | OCR fallback (optional) | >=0.3 |
| pdf2image | PDF→image for OCR pipeline (optional) | >=1.16 |

OCR dependencies (`pytesseract`, `pdf2image`) are optional and only imported when `--ocr` is used. The base tool has no dependency on Tesseract.

## Build & Distribution

### PyInstaller Build

```bash
pyinstaller \
  --onefile \
  --name pdf2md \
  --collect-all pymupdf \
  --hidden-import pymupdf4llm \
  pdf2md/__main__.py
```

The `--collect-all pymupdf` flag ensures PyMuPDF's native libraries and data files are bundled. This may need tuning per platform.

### CI/CD Matrix

Builds should run on GitHub Actions across a platform matrix:

- `ubuntu-latest` → Linux x86_64 binary
- `macos-latest` → macOS ARM64 binary
- `macos-13` → macOS x86_64 binary (if Intel support needed)
- `windows-latest` → Windows x86_64 .exe

Each build produces a release artifact. A GitHub Release bundles all platform binaries.

### Versioning

Semantic versioning. Version string lives in `pdf2md/__init__.py` and is read by both the CLI (`--version` flag) and PyInstaller build.

## Testing Strategy

### Unit Tests

- **converter.py** — test against a set of reference PDFs with known structure. Compare output markdown against expected fixtures.
- **postprocess.py** — test cleanup functions in isolation with crafted markdown strings.
- **cli.py** — use click's `CliRunner` for integration tests of the full CLI flow.

### Reference PDF Set

Maintain a `tests/fixtures/` directory with PDFs covering:

- Simple text document (paragraphs, headings)
- Document with tables
- Multi-column layout
- Document with images
- Scanned document (for OCR path)
- Document with code blocks
- Document with lists (ordered and unordered)

Each fixture PDF has a corresponding `.expected.md` file for comparison.

### Binary Testing

After PyInstaller build, run a smoke test that invokes the compiled binary against a reference PDF and verifies the output matches expectations. This catches bundling issues (missing dependencies, data files).

## Open Questions

1. **OCR scope** — should OCR be bundled into the standalone binary, or kept as a separate "install Tesseract on your system" requirement? Bundling Tesseract would significantly increase binary size (~30MB+) but improve the standalone experience.

2. **PyMuPDF licensing** — PyMuPDF uses AGPL with a commercial option from Artifex. For internal/personal use this is fine, but worth noting if the tool will be distributed commercially. The AGPL applies to PyMuPDF itself, not to PyMuPDF4LLM's Python wrapper code.

3. **Post-processing heuristics** — how aggressive should header/footer stripping be? Overly aggressive stripping risks removing legitimate repeated content. May need a `--strip-threshold` parameter.

4. **Nuitka as future option** — if binary size becomes a concern, Nuitka could produce smaller binaries. Worth revisiting once the PyInstaller pipeline is stable.
