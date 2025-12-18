# 📖 README: Antigravity Publishing Engine

This system allows you to generate professional, typeset textbooks from raw research papers using a multi-agent AI pipeline.

## 🌍 1. Cross-System Support

The "Publishing Factory" (Python Engine) is designed for portability:

| Platform | Support Level | Requirements |
| :--- | :--- | :--- |
| **macOS** | Native | Homebrew, Python 3.10+ |
| **Linux** | Native | Apt/Yum, Python 3.10+ |
| **Windows** | via WSL | Ubuntu/Debian on WSL2 |
| **Mobile/No-Code**| via Prompts | Use the "Singularity Prompt" below |

---

## 🛠️ 2. Setup & Installation

### A. Python Dependencies
Install the required libraries:
```bash
pip install -r requirements.txt
```

### B. Typesetting Stack (Optional but Recommended)
To generate the high-quality PDF:
1. **Pandoc**: The document converter.
2. **Tectonic**: The LaTeX/XeTeX engine.

### C. Directory Preparation
```bash
mkdir papers   # Put your source PDF/MD files here
mkdir book_out # Generated chapters will appear here
```

---

## 🚀 3. Usage Instructions

### A. Automatic Research Acquisition
The engine now supports autonomous research. Define your topic in the configuration block of `engine.py`:

```python
cfg = {
    "SEARCH_QUERY": "physics of agentic ai",
    "PAPER_LIMIT": "5",
    "CORPUS_PATH": "./papers"
}
```

Then simply run:
```bash
python3 engine.py
```
The engine will fetch priority papers from arXiv and immediately begin drafting the book.

### B. Compilation
To compile the generated Markdown chapters into a high-fidelity PDF:
```bash
./typeset.sh
```

---

## 🌌 4. The "Zero-Dependency" Fallback
If you are on a system without Python or LaTeX, use the **Singularity Prompt** (found in `protocols.md`). Paste it into any frontier AI (Claude 3.5, Gemini 1.5 Pro) to simulate the entire factory logic in a single turn.

---

**Built with Antigravity v1.0**
