# 📜 The Protocols: antigravity-factory core logic

This document serves as the master reference for both the **Technical Pipeline** (How the book is built) and the **Cognitive Constitution** (How the agents think).

---

## 🏛️ Part 1: The Cognitive Constitution (Anti-Slop)

All agents must adhere to the **Level 9 Hardening Protocols** defined in `grand_curation_prompt_v2.md`:

1.  **The Precision Principle**: No "vague fluff." Replace "delve" and "tapestry" with technical precision.
2.  **The Active Voice Law**: Passive voice is prohibited.
3.  **The Hemingway Enforcement**: Short sentences. Maximum clarity.
4.  **The Citation Shield**: Every claim must map to a source index `[N]`. Never hallucinate a reference.

---

## 🛠️ Part 2: The Technical Pipeline (Mastering)

The factory transforms Markdown + Mermaid into a print-ready PDF using a hybrid toolchain.

### 1. Toolchain Arch
- **Pandoc + Tectonic**: Modernized XeTeX engine for self-contained, high-fidelity PDF builds.
- **Mermaid CLI (mmdc)**: Pre-renders diagrams to high-res PNGs before LaTeX compilation.
- **Orchestrator**: `agents_orchestrator.py` manages the iterative drafting loop (Architect -> Writer -> Critic).

### 2. Build Execution
```bash
# Standard Production Build
./pdf_exporter.sh
```

---

## 🎨 Part 3: Theme Standards

The factory supports multiple global technical aesthetics:

| Theme | Benchmark | Key Visuals |
| :--- | :--- | :--- |
| **O'Reilly** | Technical Standard | Palatino/Helvetica, Woodcut art, rigorous code blocks. |
| **Springer** | Scientific Standard | Times New Roman, two-column options, minimalist academic. |
| **MIT Press** | Design Standard | Akzidenz-Grotesk, strict grid systems, avant-garde. |
| **Manning** | Industry Standard | Friendly fonts, colorful callouts, "In Action" ramps. |
| **Phrack** | Hacker Standard | JetBrains Mono, terminal aesthetics, manifesto-style. |

---

## ⚡ Part 4: Debugging & Compliance

- **Exit Code 43 (Tectonic)**: Usually caused by invalid characters in YAML. Sanitize `book_metadata.yaml`.
- **Mermaid Failures**: Often due to unclosed brackets `{}`. Audit visuals via the `critic` agent.
- **Citation Gaps**: If the `synthesis_matrix` shows a target topic has < 3 papers, mark it as a "Theoretical Bridge."

---
**© 2025 Antigravity AI Systems** | *Drafting the Future of Agentic Intelligence.*
