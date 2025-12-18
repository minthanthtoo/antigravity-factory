# Implementation Plan: Protocol Alignment & Hardening

## Goal
Enforce strict adherence to `protocols.md` across the entire codebase and documentation, eliminating "slop" and strengthening technical rigor.

## Proposed Changes

### 🏛️ System Core
#### [MODIFY] [agents_orchestrator.py](file:///Users/min/.gemini/antigravity/brain/789b4050-ebd1-435f-9527-846b3f3806b5/agents_orchestrator.py)
- **Implement `AntiSlopLinter`**: Add a method to scan generated content for banned words ("delve", "tapestry", etc.) and passive voice patterns.
- **Hardness Citation Audit**: Update the `execute_pipeline` to verify that every section meets the "3-Papers-per-Topic" requirement from the `synthesis_matrix`.
- **Merge Logic Fix**: Ensure it correctly triggers `auto_render_mermaid.py` (if applicable) or ensures `pdf_exporter.sh` handles it as per Part 2 of the protocols.

### 🧠 Cognitive Agents
#### [MODIFY] [prompts/writer.md](file:///Users/min/.gemini/antigravity/brain/789b4050-ebd1-435f-9527-846b3f3806b5/prompts/writer.md)
- Reinforce the "Hemingway Rule" and "Citation Shield" as top-level constraints.
- Explicitly list the "Disagreement Protocol" from the master constitution.

#### [MODIFY] [grand_curation_prompt_v2.md](file:///Users/min/.gemini/antigravity/brain/789b4050-ebd1-435f-9527-846b3f3806b5/grand_curation_prompt_v2.md)
- Ensure total consistency with the definitions in `protocols.md`.

### 📖 Documentation
#### [MODIFY] [README.md](file:///Users/min/.gemini/antigravity/brain/789b4050-ebd1-435f-9527-846b3f3806b5/README.md)
- Audit for active voice and precision.
- Ensure all technical descriptions match the hardened protocols.

## Verification Plan

### Automated Tests
- **Lint Test**: Run a script to scan the entire project for banned words.
- **Pipeline Test**: Run `python3 agents_orchestrator.py` in MOCK mode to verify the new linter and citation auditor triggers correctly.

### Manual Verification
- Review the generated `critic_log` during a dry run to ensure it properly identifies "slop."
