#!/bin/bash

# Configuration
METADATA="book_metadata.yaml"
CONTENT="the_physics_of_agentic_ai_full.md"
BIB="refs.bib"
PDF_OUTPUT="The_Physics_of_Agentic_AI.pdf"
HTML_OUTPUT="The_Physics_of_Agentic_AI.html"

# 1. Output Choice: Tectonic (The "Better" Choice for Scientific/Burmese)
echo "--- Step 1: Checking for PDF Engine (Tectonic) ---"

if command -v tectonic &> /dev/null; then
    echo "Tectonic found. Building Scientific PDF..."
    pandoc "$CONTENT" \
        --from markdown \
        --metadata-file="$METADATA" \
        --bibliography="$BIB" \
        --citeproc \
        -o "$PDF_OUTPUT" \
        --pdf-engine=tectonic
        
    if [ $? -eq 0 ]; then
        echo "✅ PDF Success: $PDF_OUTPUT"
        exit 0
    else
        echo "❌ PDF Build Failed (Check logs)."
    fi
else
    echo "⚠️  Tectonic not found. Skipping PDF build."
    echo "   (To get the PDF, run: brew install tectonic)"
fi

# 2. Fallback: Standalone HTML (Immediate Result)
echo ""
echo "--- Step 2: Building HTML Fallback ---"
echo "Generating standalone HTML book..."

pandoc "$CONTENT" \
    --from markdown \
    --metadata title="The Physics of Agentic AI" \
    --standalone \
    --toc \
    --bibliography="$BIB" \
    --citeproc \
    --mathjax \
    --css=https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.min.css \
    -o "$HTML_OUTPUT"

if [ $? -eq 0 ]; then
    echo "✅ HTML Success: $HTML_OUTPUT"
    echo "   You can open this in your browser immediately."
else
    echo "❌ HTML Build Failed."
fi
