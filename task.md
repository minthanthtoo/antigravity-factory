# Task: Expanding Textbook Series Scope

- [x] Categorize and rank research corpus (100 papers)
- [x] **Master Prompt Refinement**
  - [x] Implement Global Standard Themes (O'Reilly, Springer, etc.)
  - [x] Add "Phase 8: Data Annex" for theme portability
  - [x] Add "Phase 9: Anti-Slop Protocol" and "Phase 0.5: Persona Matrix"
  - [x] Centralize "User Configuration" at the top of the file
  - [x] Implement "Recursive Drafting" (Phase 3.5) and "Reading Loop" (Phase 1.5)
  - [x] Research and implement "Spiral Refinement" drafting logic (Chain of Density + Reflexion)
  - [x] Research alternative drafting strategies (ToT, Socratic, Adversarial) and Rank them
  - [x] Implement `DRAFTING_MODE` selector in Master Prompt
  - [x] Implement "Phase 1.3: The Synthesis Matrix" (Topic-Source Mapping)
  - [x] Add "Thesis Grinder" logic for handling ultra-long documents
  - [x] Finalize "Grand Curation Prompt v2.2"
  - [x] **Level 2: Systemic Architecture (The Fix)**
    - [x] Create `orchestrator_harness.py` (Python Runtime for PDF Chunking)
    - [x] Split Master Prompt into `prompts/architect.md` (Strategy)
    - [x] Split Master Prompt into `prompts/writer.md` (Execution)
    - [x] Split Master Prompt into `prompts/critic.md` (Review)
- [x] Final Alignment Audit and Cross-Referencing
- [x] Generate Walkthrough and Proof of Rigor

## PDF Generation & Aesthetics
- [x] **Typography & Layout**
    - [x] Configure Pandoc metadata (`book_metadata.yaml`)
    - [x] Implement "O'Reilly-like" premium styling (Titlesec, Fancyhdr)
    - [x] Fix font pipeline (Fontspec order, Latin Modern defaults)
    - [x] Integrate Noto Sans Myanmar for Burmese text segments
- [x] **Visuals & Diagrams**
    - [x] Implement pre-rendering strategy for Mermaid diagrams
    - [x] Apply "Neutral" theme for professional appearance
    - [x] Ensure correct scaling (90% width) and centering
- [x] **Final Build**
    - [x] Generate complete PDF (The_Physics_of_Agentic_AI.pdf)

## O'Reilly Styling & Artwork Overhaul
- [x] **Advanced Typography & Layout**
    - [x] Update Fonts: Palatino (Body), Helvetica (Headers), Inconsolata (Code)
    - [x] Style Reference Lines & Lists (Clean, compact)
    - [x] Fancy TOC: styled sizing, bullets, and layout
- [x] **Diagram & Code Styling**
    - [x] Create `mermaid.css` for clean, professional book diagrams (borders, arrows, fonts)
    - [x] Refine `mermaid.css` for strict O'Reilly technical look (sharper lines, specific fonts)
    - [x] Update `auto_render_mermaid.py` to use custom CSS
    - [x] Configure Code Blocks: Background color, distinct coding font (Courier enforced)
- [x] **Artwork Generation**
    - [x] Extract keywords for cover art
    - [x] Generate Cover Art (AI-generated)
- [x] **Final Polish Build**
    - [x] Re-run full build with new styles (Cycle 5)

## 🛠️ Level 9: Strategic Autonomy & Documentation
- [x] Level 9: Strategic Drift & Cognitive Pathologies (Architect Review, Citation Preservation)
- [x] Documentation & Handover
    - [x] Create Single Prompt "Bootstrap" for cross-AI portability
    - [x] Verify PDF/HTML Build Pipeline
    - [x] Create comprehensive "User Guide" (usage.md)
- [x] Paper Acquisition Engine
    - [x] Implement `fetch_papers.py` (arXiv Search & Download)
    - [x] Integrate with `requirements.txt`
    - [x] Update `README.md` with acquisition instructions
- [x] Unified Engine Merge
    - [x] Integrate search logic into `agents_orchestrator.py`
    - [x] Implement autonomous "Phase 0" research step
    - [x] Cleanup standalone scripts
- [x] Naming System Refactor
    - [x] Rename core components (Orchestrator, Curator, Master Template, Typeset)
    - [x] Update internal references and documentation
