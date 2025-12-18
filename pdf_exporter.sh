#!/bin/bash
# antigravity-factory Production PDF Builder

INPUT="the_physics_of_agentic_ai_full.md"
OUTPUT_PDF="The_Physics_of_Agentic_AI.pdf"
OUTPUT_HTML="The_Physics_of_Agentic_AI.html"
METADATA="book_metadata.yaml"

echo "🚀 Starting Production Export..."

# 1. Generate Metadata if missing
if [ ! -f "$METADATA" ]; then
cat <<EOF > "$METADATA"
---
title: "The Physics of Agentic AI"
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
fi

# 2. PDF Export (Tectonic)
if command -v pandoc &> /dev/null && command -v tectonic &> /dev/null; then
    echo "📄 Generating PDF via Tectonic..."
    pandoc "$INPUT" \
        --metadata-file="$METADATA" \
        --toc \
        --pdf-engine=tectonic \
        -o "$OUTPUT_PDF"
    echo "✅ PDF Success: $OUTPUT_PDF"
else
    echo "⚠️  Pandoc or Tectonic not found. Skipping PDF."
fi

# 3. HTML Export
if command -v pandoc &> /dev/null; then
    echo "🌐 Generating HTML Preview..."
    pandoc "$INPUT" \
        --metadata-file="$METADATA" \
        --toc \
        --self-contained \
        -o "$OUTPUT_HTML"
    echo "✅ HTML Success: $OUTPUT_HTML"
fi
