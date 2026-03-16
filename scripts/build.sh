#!/bin/bash
set -euo pipefail

echo "Building pdf2md standalone binary..."

pyinstaller \
    --onefile \
    --name pdf2md \
    --collect-all pymupdf \
    --hidden-import pymupdf4llm \
    --exclude-module pytesseract \
    --exclude-module pdf2image \
    --exclude-module tkinter \
    pdf2md/__main__.py

echo ""
echo "Build complete. Binary at: dist/pdf2md"
echo ""

# Smoke test
echo "Running smoke test..."
./dist/pdf2md --version
echo "Smoke test passed."
