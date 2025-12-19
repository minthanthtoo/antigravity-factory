#!/bin/bash
# antigravity-factory Production PDF Builder

# antigravity-factory Production PDF Builder

# Accept Book Name from Argument
BOOK_NAME="${1:-The Physics of Agentic AI}"
FILE_BASENAME=$(echo "$BOOK_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | sed 's/[^a-z0-9_]//g')

INPUT="${FILE_BASENAME}_full.md"
OUTPUT_PDF="${BOOK_NAME// /_}.pdf"
OUTPUT_HTML="${BOOK_NAME// /_}.html"
METADATA="book_metadata.yaml"

echo "Starting Production Export for: $BOOK_NAME"

# 1. Generate Metadata
cat <<EOF > "$METADATA"
---
title: "$BOOK_NAME"
author: "Antigravity Research Factory"
date: "$(date +%Y-%m-%d)"
geometry: margin=1in
fontsize: 11pt
header-includes:
  - \usepackage{palatino}
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhead[R]{\thepage}
---
EOF

# 2. PDF Export (Tectonic)
if command -v pandoc &> /dev/null && command -v tectonic &> /dev/null; then
    echo "Generating PDF via Tectonic..."
    pandoc "$INPUT" \
        --metadata-file="$METADATA" \
        --toc \
        --pdf-engine=tectonic \
        -o "$OUTPUT_PDF"
    echo "PDF Success: $OUTPUT_PDF"
else
    echo "WARNING: Pandoc or Tectonic not found. Skipping PDF."
fi

# 3. HTML Export
if command -v pandoc &> /dev/null; then
    echo "Generating HTML Preview..."
    pandoc "$INPUT" \
        --metadata-file="$METADATA" \
        --toc \
        --self-contained \
        -o "$OUTPUT_HTML"
    echo "HTML Success: $OUTPUT_HTML"
fi
