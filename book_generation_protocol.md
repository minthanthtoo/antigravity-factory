# Master Book Generation Protocol

This document codifies the process, tools, and prompts used to generate high-quality, aesthetically styling technical books from Markdown content.

## 1. Toolchain Configuration

The pipeline transforms raw Markdown + Mermaid diagrams into a print-ready PDF using a hybrid toolchain.

### Core Components
- **Pandoc**: The universal document converter.
- **Tectonic**: A modernized, self-contained LaTeX engine (based on XeTeX).
- **Mermaid CLI (mmdc)**: For pre-rendering diagrams to high-res PNGs.
- **Python Glue Code**: `auto_render_mermaid.py` to orchestrate diagram extraction and replacement.

### The Build Command
```bash
python3 auto_render_mermaid.py && \
pandoc input.md -o output.pdf \
    --pdf-engine=tectonic \
    --metadata-file=book_metadata.yaml \
    --include-in-header=preamble.tex \
    --highlight-style=tango \
    --bibliography=refs.bib \
    --citeproc
```

## 2. Creative Styling Prompts (Theme Selection)

Use the `THEME_MODE` variable in the Master Prompt to trigger these specific aesthetics.

### Theme A: "The Technical Standard" (O'Reilly Style)
- **Benchmark**: O'Reilly Media / Pearson.
- **Visuals**: Palatino/Helvetica/Courier. Clean, distinct lines. Woodcut cover art.
- **Vibe**: Authoritative, production-ready, engineering-focused.

### Theme B: "The Scientific Standard" (Springer/Nature Style)
- **Benchmark**: Springer / Elsevier / IEEE.
- **Visuals**: Times New Roman/Minion Pro. Two-column layout options. Minimalist "academic" figures.
- **Vibe**: Rigorous, peer-reviewed, theoretical density.

### Theme C: "The Design Standard" (MIT Press / Swiss Style)
- **Benchmark**: MIT Press / Taschen.
- **Visuals**: Akzidenz-Grotesk/Helvetica Neue. Strict grid systems. Abstract geometric art.
- **Vibe**: Modernist, avant-garde, "Art of Code".

### Theme D: "The Industry Standard" (Manning / Packt Style)
- **Benchmark**: Manning "In Action" / Packt.
- **Visuals**: Open Sans/Charter. Friendly serif/sans mixes. Colorful icons and callouts.
- **Vibe**: Practical, tutorial-heavy, "Zero-to-Hero" ramps.

### Theme E: "The Hacker Standard" (Cyberpunk Style)
- **Benchmark**: Phrack / 2600 / Stripe Press (High-end).
- **Visuals**: JetBrains Mono headers. Terminal aesthetics. Glitch art.
- **Vibe**: Counter-culture, edge-case, manifesto.

## 3. Style Debugging Guide (The Tectonic Protocol)

When the PDF build fails (Exit Code 43), follow this debugging protocol:

1.  **The "Missing \begin{document}" Error**:
    - **Cause**: Invalid characters in YAML metadata (often `#` comments interpreted as text).
    - **Fix**: Move all styling logic to `preamble.tex`. Keep `book_metadata.yaml` minimal (Title, Author, Geometry only).

2.  **The "Font Not Found" Error**:
    - **Cause**: Tectonic cannot find system fonts by name (e.g., "TeX Gyre Pagella").
    - **Fix**: Use standard LaTeX packages (`\usepackage{mathpazo}`) instead of `fontspec` file naming (`\setmainfont{...}`).

3.  **Mermaid Scaling Issues**:
    - **Cause**: Diagrams too wide for PDF page.
    - **Fix**: In the Python script, wrap images in a LaTeX center environment and add `{width=80%}` to the Markdown link.

## 4. Automation Scripts

### `auto_render_mermaid.py`
Key features:
- Regex extraction of `mermaid` blocks.
- `mmdc` execution with `--theme neutral` and `--cssFile mermaid.css`.
- Replacement with `![Diagram](path.png){width=80%}` inside `\begin{center}` environment.

### `cover_art_gen.py` (Concept)
- Uses `generate_image` tool.
- Prompt strategy: "Woodcut/Engraving style" for technical books, "Abstract Geometric" for theoretical books.
