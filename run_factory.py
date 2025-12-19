#!/usr/bin/env python3
import argparse
from agents_orchestrator import ConfigManager, Orchestrator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Factory v1.0")
    # Copy arguments definitions from original or just pass through?
    # Ideally reuse ConfigManager logic.
    # We will just instantiate the ConfigManager which handles args inside its load method if we pass namespaces,
    # But ConfigManager.load expects an argparse.Namespace.
    # To avoid duplicating arg definitions, we should probably expose the parser setup in agents_orchestrator.py or just replicate basic ones here.
    # PROPER WAY: Let's import the parser from agents_orchestrator if possible, or just re-define.
    # Given the previous code, the parser definition was inside `if __name__ == "__main__"`.
    # So we must re-define them here to expose CLI to user.
    
    parser.add_argument("-n", "--book-name", help="Specific title for the book")
    parser.add_argument("-k", "--keywords", help="Keywords for search and naming")
    parser.add_argument("-g", "--goal", help="Research goal for synthesis and naming")
    parser.add_argument("-c", "--corpus", help="Path to research papers")
    parser.add_argument("-o", "--output", help="Path for generated chapters")
    parser.add_argument("-l", "--limit", type=int, help="Maximum number of papers to fetch")
    parser.add_argument("-f", "--fetch-mode", choices=["fulltext", "abstract"], help="Fetch full PDF or just abstract/metadata")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm all downloads")
    parser.add_argument("-m", "--mock", action="store_true", help="Enable explicit mock mode")
    parser.add_argument("-a", "--after", help="Fetch papers published AFTER this date (YYYY-MM-DD)")
    parser.add_argument("-b", "--before", help="Fetch papers published BEFORE this date (YYYY-MM-DD)")
    parser.add_argument("-B", "--between", help="Fetch papers published BETWEEN these dates")
    parser.add_argument("-S", "--sources", help="Comma-separated list of sources")
    parser.add_argument("-F", "--format", choices=["pdf", "html", "epub", "docx", "latex", "json", "md"], help="Final output format")

    args = parser.parse_args()
    try:
        cfg = ConfigManager.load(args)
        Orchestrator(cfg).execute_pipeline()
        print("\n✅ \033[0;32mFactory Pipeline Complete.\033[0m")
    except KeyboardInterrupt:
        print("\n\n⚠️ \033[0;33mPipeline interrupted by user.\033[0m")
    except Exception as e:
        print(f"\n❌ \033[0;31mPipeline Failed: {e}\033[0m")
