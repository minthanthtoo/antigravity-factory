import os
import sys
import glob
import logging
import re
import time
import subprocess
import argparse
from typing import Dict, List

try:
    from paper_fetcher import ResearchEngine
except ImportError as e:
    logging.warning(f"ResearchEngine Import Failed: {e}")
    ResearchEngine = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LocalIntelligence:
    """Fallback Engine using Local Transformer Models."""
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = "cpu"
        if os.uname().sysname == "Darwin":
             # Check for Apple Silicon
             try:
                 import torch
                 if torch.backends.mps.is_available():
                     self.device = "mps"
             except: pass
        
    def assess_hardware(self) -> Dict:
        import subprocess
        try:
            ram_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
            ram_gb = ram_bytes / (1024**3)
        except:
            ram_gb = 8 # Assumption if check fails
            
        rec = {
            "ram_gb": round(ram_gb, 1),
            "recommended_model": "google/gemma-2b-it",
            "reason": "Fits in 8GB RAM (FP16)"
        }
        
        if ram_gb >= 16:
            rec["recommended_model"] = "google/gemma-7b-it"
            rec["reason"] = "High RAM detected, using 7B model."
        elif ram_gb < 8:
            rec["recommended_model"] = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            rec["reason"] = "Low RAM detected, using TinyLlama."
            
        return rec

    def load_engine(self, model_id: str):
        logging.info(f"⚙️ Loading Local Model: {model_id} on {self.device}...")
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            import torch
            
            dtype = torch.float16 if self.device in ["mps", "cuda"] else torch.float32
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                torch_dtype=dtype,
                device_map=self.device if self.device != "mps" else None # HF accelerate handles mps poorly sometimes, manual to come
            )
            if self.device == "mps":
                self.model.to("mps")
                
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=2048
            )
            logging.info("✅ Local Engine Online.")
        except Exception as e:
            logging.error(f"Failed to load local model: {e}")
            raise

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "user", "content": f"{system_prompt}\n\nTask: {user_prompt}"}
        ]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = self.pipeline(prompt, do_sample=True, temperature=0.7)
        return outputs[0]["generated_text"][len(prompt):]

class AntiSlopLinter:
    """Phase 9: Anti-Slop & Precision Protocol Enforcement."""
    BANNED_WORDS = ["delve", "showcase", "underscore", "testament", "rich tapestry", "landscape", "pave the way"]
    
    @classmethod
    def lint(cls, text: str) -> List[str]:
        issues = []
        # Check for banned words
        for word in cls.BANNED_WORDS:
            if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                issues.append(f"Anti-Slop Violation: Banned word '{word}' found.")
        
        # Check for passive voice (simple heuristic)
        passive_patterns = [
            r'\b(is|am|are|was|were|be|been|being)\b\s+\b([a-z]+ed)\b',
            r'\b(has|have|had)\b\s+been\s+\b([a-z]+ed)\b'
        ]
        for pattern in passive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Only flag as a minor warning for now, as passive voice isn't always wrong
                # but we want to minimize it as per Protocol Part 1.2
                issues.append("Passive Voice Warning: Consider active voice.")
        
        return issues

class TokenCounter:
    """Fix Level 8.3: Cost Safety."""
    def __init__(self, budget: int = 5000000):
        self.total_tokens = 0
        self.budget = budget

    def add(self, text: str):
        count = len(text) // 4
        self.total_tokens += count
        if self.total_tokens > self.budget:
            raise Exception(f"❌ Token Budget Exceeded ({self.total_tokens} > {self.budget}).")
        return count

class CitationAuditor:
    """Phase 1.3: Citation Shield Enforcement."""
    @classmethod
    def audit(cls, text: str, matrix_refs: int = 0) -> List[str]:
        issues = []
        citations = re.findall(r'\[\d+\]', text)
        unique_citations = set(citations)
        
        if len(unique_citations) < 3 and matrix_refs >= 3:
            issues.append(f"Citation Shield Gap: Only {len(unique_citations)} unique sources cited (Target: 3+).")
        
        return issues

class ConfigManager:
    """Fix Level 9.2: Persistent Configuration."""
    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "factory_config.json")

    @classmethod
    def load(cls, cli_args: argparse.Namespace) -> Dict:
        # 1. Base Defaults
        config = {
            "SOURCES": "arxiv,semanticscholar,crossref",
            "PAPER_LIMIT": 5,
            "FETCH_MODE": "fulltext",
            "OUTPUT_FORMAT": "pdf",
            "MOCK_MODE": False,
            "CORPUS_PATH": "./papers",
            "OUTPUT_PATH": "./book_out"
        }

        # 2. File Defaults (factory_config.json)
        if os.path.exists(cls.DEFAULT_CONFIG_PATH):
            try:
                import json
                with open(cls.DEFAULT_CONFIG_PATH, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                logging.warning(f"Failed to load config file: {e}")

        # 3. CLI Overrides (Only if user provided them)
        if hasattr(cli_args, 'book_name') and cli_args.book_name: config["BOOK_NAME"] = cli_args.book_name
        if hasattr(cli_args, 'keywords') and cli_args.keywords: config["KEYWORDS"] = cli_args.keywords
        if hasattr(cli_args, 'goal') and cli_args.goal: config["RESEARCH_GOAL"] = cli_args.goal
        if hasattr(cli_args, 'corpus') and cli_args.corpus: config["CORPUS_PATH"] = cli_args.corpus
        if hasattr(cli_args, 'output') and cli_args.output: config["OUTPUT_PATH"] = cli_args.output
        if hasattr(cli_args, 'limit') and cli_args.limit is not None: config["PAPER_LIMIT"] = cli_args.limit
        if hasattr(cli_args, 'fetch_mode') and cli_args.fetch_mode: config["FETCH_MODE"] = cli_args.fetch_mode
        if hasattr(cli_args, 'yes') and cli_args.yes: config["AUTO_CONFIRM"] = cli_args.yes
        if hasattr(cli_args, 'mock') and cli_args.mock: config["MOCK_MODE"] = cli_args.mock
        if hasattr(cli_args, 'sources') and cli_args.sources: config["SOURCES"] = cli_args.sources
        if hasattr(cli_args, 'format') and cli_args.format: config["OUTPUT_FORMAT"] = cli_args.format

        # Handle dates with safe attribute access
        start_date = getattr(cli_args, 'after', None)
        end_date = getattr(cli_args, 'before', None)
        between = getattr(cli_args, 'between', None)
        
        if between:
            parts = between.split(",")
            if len(parts) == 2:
                start_date, end_date = parts[0].strip(), parts[1].strip()
        
        if start_date: config["START_DATE"] = start_date
        if end_date: config["END_DATE"] = end_date
        
        if not config.get("SEARCH_QUERY"):
            if config.get("KEYWORDS"): config["SEARCH_QUERY"] = config["KEYWORDS"]
            elif config.get("RESEARCH_GOAL"): config["SEARCH_QUERY"] = config["RESEARCH_GOAL"]

        return config

class Orchestrator:
    def __init__(self, user_config: Dict):
        self.user_config = user_config
        self.corpus_path = user_config.get("CORPUS_PATH", "./papers")
        self.output_path = user_config.get("OUTPUT_PATH", "./book_out")
        self.book_name = user_config.get("BOOK_NAME", "The Physics of Agentic AI")
        self.prompts = self._load_prompts()
        self.counter = TokenCounter(budget=user_config.get("TOKEN_BUDGET", 5000000))
        
        # Load Master Reference
        self.master_ref = ""
        v2_path = os.path.join(os.path.dirname(__file__), "grand_curation_prompt_v2.md")
        if os.path.exists(v2_path):
            with open(v2_path, 'r', encoding='utf-8') as f:
                self.master_ref = f.read()

        self.mock_enabled = self.user_config.get("MOCK_MODE", False)
        self.local_brain = LocalIntelligence()
        self.book_name = self._determine_book_name()
        self._validate_environment()

    def _determine_book_name(self) -> str:
        """Resolve the book name via CLI override or LLM generation."""
        cli_name = self.user_config.get("BOOK_NAME")
        if cli_name:
            return cli_name

        keywords = self.user_config.get("KEYWORDS")
        goal = self.user_config.get("RESEARCH_GOAL")
        
        if keywords or goal:
            logging.info("Generating dynamic book name based on keywords/goal...")
            prompt = f"Based on the keywords '{keywords}' and research goal '{goal}', generate a short, academic, and industrial book title. Output ONLY the title."
            title = self._call_llm("Role: Naming Expert", prompt).strip().strip('"').strip("'")
            if title and "Error" not in title:
                return title
        
        return "The Physics of Agentic AI" # Default fallback

    def _validate_environment(self):
        # API Key precedence: CLI/Config > Environment
        api_key = self.user_config.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        has_key = api_key is not None or "OPENAI_API_KEY" in os.environ
        
        if not has_key and not self.mock_enabled:
            print("\n⚠️  Security Alert: Real Mode active but no API Key found.")
            print("You have two options:")
            print("1. Enter GOOGLE_API_KEY")
            print("2. Download/Use Local LLM (HuggingFace)")
            
            try:
                choice = input("Enter Key or press [L] for Local LLM: ").strip()
                if choice.lower() == 'l':
                    rec = self.local_brain.assess_hardware()
                    print(f"\n🖥️  Hardware Check: {rec['ram_gb']}GB RAM Detected.")
                    print(f"💡 Recommended: {rec['recommended_model']} ({rec['reason']})")
                    
                    ans = input(f"Download and load {rec['recommended_model']}? [Y/n]: ").strip().lower()
                    if ans != 'n':
                        model = input(f"Confirm model ID (default: {rec['recommended_model']}): ").strip() or rec['recommended_model']
                        self.local_brain.load_engine(model)
                    else:
                        raise Exception("Aborted by user.")
                elif choice:
                    self.user_config["GOOGLE_API_KEY"] = choice
                    os.environ["GOOGLE_API_KEY"] = choice
                    logging.info("API Key injected into runtime.")
                else:
                    raise Exception("No key provided. Aborting.")
            except EOFError:
                raise Exception("CRITICAL ERROR: No API Key found and non-interactive environment.")
        
        if ResearchEngine is None and "SEARCH_QUERY" in self.user_config:
            logging.warning("WARNING: 'paper_fetcher' module not found. Search functionality will be disabled.")

    def _acquire_papers(self, query: str, limit: int = 5, start_date: str = None, end_date: str = None, fetch_mode: str = "fulltext", auto_confirm: bool = False, sources: List[str] = ["arxiv"]):
        """Trigger the modular Research Engine."""
        if ResearchEngine is None:
            logging.error("ERROR: Cannot acquire papers: ResearchEngine module missing.")
            return

        engine = ResearchEngine(self.corpus_path)
        engine.search_and_download(query, limit, start_date=start_date, end_date=end_date, fetch_mode=fetch_mode, auto_confirm=auto_confirm, sources=sources)

    def _load_prompts(self) -> Dict[str, str]:
        prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")
        prompts = {}
        for role in ["architect", "writer", "critic", "summarizer"]:
            path = os.path.join(prompt_dir, f"{role}.md")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    prompts[role] = f.read()
        return prompts

    def _render_prompt(self, template: str, context: Dict[str, str]) -> str:
        rendered = template
        full_context = {**self.user_config, **context}
        for key, value in full_context.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def ask_antigravity(self, message: str) -> str:
        """
        Public programmatic interface to query the Antigravity Brain.
        Useful for internal scripts wanting to leverage the configured factory intelligence.
        """
        logging.info(f"Antigravity Query: {message}")
        return self._call_llm_with_retry("Role: Intelligent Assistant. Answer the user's question directly.", message)

    def _call_llm_with_retry(self, system_prompt: str, user_content: str, max_retries: int = 3) -> str:
        full_system_prompt = f"{self.master_ref}\n\n### SPECIFIC AGENT ROLE:\n{system_prompt}"
        self.counter.add(full_system_prompt + user_content)
        attempt = 0
        last_error = None
        while attempt < max_retries:
            try:
                # FIX: Mock Mode Verification FIRST
                if self.mock_enabled:
                    return self._mock_llm_response(full_system_prompt)
                
                # Check config OR env for key
                if self.user_config.get("GOOGLE_API_KEY") or "GOOGLE_API_KEY" in os.environ:
                    response = self._call_real_gemini(full_system_prompt, user_content)
                    self.counter.add(response)
                    return response
                else:
                    raise Exception("No API keys found in Config or Environment, and Mock Mode is OFF.")
            except Exception as e:
                attempt += 1
                last_error = str(e)
                wait_time = 2 ** attempt
                logging.error(f"API Error: {e}. Retry {attempt}/{max_retries}...")
                time.sleep(wait_time)
        return f"Critical API Failure: {last_error}"

    def _call_real_gemini(self, system_prompt: str, user_content: str) -> str:
        try:
            import google.generativeai as genai
            api_key = self.user_config.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)
            model_name = self.user_config.get("MODEL_NAME", "gemini-3-flash-preview")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(f"SYSTEM: {system_prompt}\nUSER: {user_content}")
            return response.text
        except ImportError:
            if "GOOGLE_API_KEY" in os.environ: raise Exception("❌ Library missing.")
            return self._mock_llm_response(system_prompt)

    def _mock_llm_response(self, system_prompt: str) -> str:
        time.sleep(0.1)
        role_part = system_prompt.split("### SPECIFIC AGENT ROLE:")[-1]
        
        if "# The Architect" in role_part or "# 🏗️ The Architect" in role_part:
            return "<synthesis_matrix>\n<topic name='Foundation'>\n<source id='1'>Logic</source>\n<source id='2'>Reasoning</source>\n<source id='3'>Tools</source>\n</topic>\n</synthesis_matrix>\n## Outline\n- Introduction"
        
        if "# The Writer" in role_part or "# ✍️ The Writer" in role_part:
            return "# Chapter Content\nThe system executes the logic described in [1], [2], and [3]. This approach ensures technical rigor."
        
        if "# The Critic" in role_part or "# 🧪 The Critic" in role_part:
            return "Status: PASS"
            
        if "Role: Naming Expert" in system_prompt:
            return "Autonomous Intelligence: The Industrial Frontier"
            
        return "Summary preserving [1], [2], and [3]."

    _call_llm = _call_llm_with_retry

    def _lint_latex_safety(self, text: str) -> str:
        protected = [r'```.*?```', r'~~~.*?~~~', r'`.*?`']
        parts = re.split(f"({'|'.join(protected)})", text, flags=re.DOTALL)
        clean = []
        for p in parts:
            if not p: continue
            if any(re.match(pat, p, re.DOTALL) for pat in protected): clean.append(p)
            else: clean.append(p.replace("%", "\\%").replace("$", "\\$").replace("&", "\\&"))
        return "".join(clean)

    def _validate_mermaid(self, text: str) -> bool:
        blocks = re.findall(r'```mermaid(.*?)```', text, re.DOTALL)
        for b in blocks:
            if b.count("{") != b.count("}") or b.count("(") != b.count(")"): return False
        return True

    def execute_pipeline(self):
        logging.info("Starting Pipeline...")
        
        # Phase 0: Acquisition
        if "SEARCH_QUERY" in self.user_config:
            self._acquire_papers(self.user_config["SEARCH_QUERY"], 
                                int(self.user_config.get("PAPER_LIMIT", 5)),
                                start_date=self.user_config.get("START_DATE"),
                                end_date=self.user_config.get("END_DATE"),
                                fetch_mode=self.user_config.get("FETCH_MODE", "fulltext"),
                                auto_confirm=self.user_config.get("AUTO_CONFIRM", False))

        docs = glob.glob(os.path.join(self.corpus_path, "**/*.pdf"), recursive=True) + glob.glob(os.path.join(self.corpus_path, "**/*.md"), recursive=True)
        pdf_docs = [d for d in docs if d.endswith(".pdf")]

        if not pdf_docs:
            print("\033[0;33mWARNING: No PDF papers found in corpus path.\033[0m")
            print("\033[0;36mTIP: Use '--corpus /path/to/pdfs' to specify a directory containing your research PDFs.\033[0m")
        
        if not docs:
            if self.mock_enabled:
                logging.info("Mock mode enabled: No papers found. Proceeding with mock synthesis to test export pipeline.")
            else:
                print("\033[0;31mERROR: No research papers found in corpus path.\033[0m")
                try:
                    query = input("\nEnter search keywords/topics to acquire research (or press Enter for MOCK): ").strip()
                    if query:
                        logging.info(f"Initiating adaptive search for: {query}")
                        self._acquire_papers(query, 
                                            int(self.user_config.get("PAPER_LIMIT", 5)),
                                            start_date=self.user_config.get("START_DATE"),
                                            end_date=self.user_config.get("END_DATE"),
                                            fetch_mode=self.user_config.get("FETCH_MODE", "fulltext"),
                                            auto_confirm=self.user_config.get("AUTO_CONFIRM", False),
                                            sources=self.user_config.get("SOURCES", "arxiv").split(","))
                        # Rescan docs
                        docs = glob.glob(os.path.join(self.corpus_path, "**/*.pdf"), recursive=True) + glob.glob(os.path.join(self.corpus_path, "**/*.md"), recursive=True)
                        if not docs:
                            logging.warning("WARNING: Search returned no results. Falling back to MOCK SYNTHESIS.")
                    else:
                        logging.warning("WARNING: No search query provided. Falling back to MOCK SYNTHESIS for demonstration.")
                except EOFError:
                    logging.warning("WARNING: Non-interactive environment detected. Falling back to MOCK SYNTHESIS.")

        manifest = {"chapters": {}, "status": "IN_PROGRESS"} 
        
        # Step 1: Architect
        arch_p = self._render_prompt(self.prompts["architect"], {"CORPUS_CONTEXT": "Initial docs"})
        arch_out = self._call_llm(arch_p, "Design blueprint.")
        blueprint = re.search(r"##\s+Outline(.*)", arch_out, re.DOTALL | re.IGNORECASE).group(1).strip() if "## Outline" in arch_out else "Default Outline"
        
        # Step 2: Writer Loop
        chapters = ["Chapter 1: Foundation", "Chapter 2: Logic"]
        prev_summ = "None"
        for i, ch in enumerate(chapters):
            if i > 0 and i % 5 == 0: 
                rev_p = self._render_prompt(self.prompts["architect"], {"CORVIOUS_PROGRESS": prev_summ, "CURRENT_BLUEPRINT": blueprint})
                arch_out = self._call_llm(rev_p, "Update.")
                blueprint = arch_out 

            logging.info(f"Drafting {ch}...")
            base_p = self._render_prompt(self.prompts["writer"], {"CHAPTER_TITLE": ch, "BLUEPRINT": blueprint, "PREVIOUS_CHAPTER_SUMMARY": prev_summ})
            
            ok, retries, hist = False, 0, [] 
            while not ok and retries < 3:
                draft = self._call_llm(base_p, f"Draft {ch}")
                
                # Protocol Hardening Pass
                lint_issues = AntiSlopLinter.lint(draft)
                # Heuristic: count intended refs from matrix (if accessible)
                citation_issues = CitationAuditor.audit(draft, matrix_refs=3) 
                
                if not self._validate_mermaid(draft): critique = "FAIL: Visuals (Broken Mermaid Syntax)."
                elif lint_issues: critique = f"FAIL: Protocol Violation. {lint_issues[0]}"
                elif citation_issues: critique = f"FAIL: {citation_issues[0]}"
                else: 
                    critic_p = self._render_prompt(self.prompts["critic"], {"PREVIOUS_CRITIQUES": "\n".join(hist)})
                    critique = self._call_llm(critic_p, draft)
                
                hist.append(critique)
                if "Status: PASS" in critique: ok = True
                else: 
                    retries += 1
                    base_p += f"\n\nLATEST PROTOCOL FEEDBACK: {critique}"
            
            if ok:
                self.save_chapter(ch, self._lint_latex_safety(draft))
                manifest["chapters"][ch] = "READY"
                s_p = self._render_prompt(self.prompts["summarizer"], {"CHAPTER_CONTENT": draft})
                prev_summ = self._call_llm(s_p, "Summarize.")
            else:
                logging.error(f"FAILURE: Could not draft {ch} after {retries} retries.")
                logging.error(f"Reason chain: {hist}")
                manifest["status"] = "BROKEN"
                break

        if manifest["status"] == "IN_PROGRESS": manifest["status"] = "READY"
        
        if manifest["status"] == "READY":
            self.trigger_build_pipeline(manifest)
        else:
            logging.error("ABORTED: Incomplete Manifest.")

    def _sanitize_filename(self, text: str) -> str:
        # Remove colons, replace spaces, keep alphanumeric/dashes
        # Example: "Chapter 2: Logic" -> "chapter_2_logic"
        stage_1 = text.lower().replace(" ", "_").replace(":", "").replace("/", "_")
        return re.sub(r'[^a-z0-9_.-]', '', stage_1)

    def trigger_build_pipeline(self, manifest: Dict):
        # 1. Setup Isolated Build Directory
        safe_name = self._sanitize_filename(self.book_name)
        build_dir = os.path.join(self.output_path, safe_name)
        os.makedirs(build_dir, exist_ok=True)
        
        logging.info(f"🧵 Stitching master file in: {build_dir}")
        master_fn = f"{safe_name}_full.md"
        master_path = os.path.join(build_dir, master_fn)
        
        try:
            # 2. Stitch Chapters
            with open(master_path, 'w', encoding='utf-8') as master:
                for ch in manifest["chapters"].keys():
                    fn = f"{self._sanitize_filename(ch)}.md"
                    src_path = os.path.join(build_dir, fn)
                    if os.path.exists(src_path):
                        with open(src_path, 'r', encoding='utf-8') as f:
                            master.write(f.read() + "\n\n")
            
            # 3. Create Bibliography
            bib_path = os.path.join(build_dir, "refs.bib")
            if not os.path.exists(bib_path):
                with open(bib_path, 'w') as f: f.write("@misc{placeholder, title={Placeholder}}")

            # 4. Trigger Export
            output_fmt = self.user_config.get("OUTPUT_FORMAT", "pdf")
            script = os.path.join(os.path.dirname(__file__), "pdf_exporter.sh")
            abs_script = os.path.abspath(script)
            
            if output_fmt == "pdf":
                if os.path.exists(script):
                    subprocess.run(["bash", abs_script, self.book_name], cwd=build_dir)
                    logging.info(f"📚 PDF Generation finished in {build_dir}")
                else:
                    logging.warning("⚠️ pdf_exporter.sh not found. Skipping PDF build.")
            
            elif output_fmt == "epub":
                logging.info(f"Generating EPUB for {safe_name}...")
                subprocess.run(["pandoc", master_fn, "-o", f"{safe_name}.epub", "--metadata", f"title={self.book_name}"], cwd=build_dir)
                
            elif output_fmt == "docx":
                logging.info(f"Generating DOCX for {safe_name}...")
                subprocess.run(["pandoc", master_fn, "-o", f"{safe_name}.docx", "--metadata", f"title={self.book_name}"], cwd=build_dir)
                
            elif output_fmt == "latex":
                logging.info(f"Generating LaTeX for {safe_name}...")
                subprocess.run(["pandoc", master_fn, "-o", f"{safe_name}.tex", "--metadata", f"title={self.book_name}"], cwd=build_dir)

            elif output_fmt == "json":
                logging.info("JSON Metadata export skipped (managed by catalog).")

        except Exception as e:
            logging.error(f"❌ Mastering failed: {e}")

    def save_chapter(self, title: str, content: str):
        # Save to isolated build directory
        safe_name = self._sanitize_filename(self.book_name)
        build_dir = os.path.join(self.output_path, safe_name)
        os.makedirs(build_dir, exist_ok=True)
        
        fn = f"{self._sanitize_filename(title)}.md"
        with open(os.path.join(build_dir, fn), 'w', encoding='utf-8') as f: f.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="antigravity-factory Orchestrator")
    parser.add_argument("-n", "--book-name", help="Specific title for the book")
    parser.add_argument("-k", "--keywords", help="Keywords for search and naming")
    parser.add_argument("-g", "--goal", help="Research goal for synthesis and naming")
    parser.add_argument("-c", "--corpus", help="Path to research papers")
    parser.add_argument("-o", "--output", help="Path for generated chapters")
    parser.add_argument("-l", "--limit", type=int, help="Maximum number of papers to fetch")
    parser.add_argument("-f", "--fetch-mode", choices=["fulltext", "abstract"], help="Fetch full PDF or just abstract/metadata")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm all downloads")
    parser.add_argument("-m", "--mock", action="store_true", help="Enable explicit mock mode (simulated LLM responses)")
    parser.add_argument("-a", "--after", help="Fetch papers published AFTER this date (YYYY-MM-DD)")
    parser.add_argument("-b", "--before", help="Fetch papers published BEFORE this date (YYYY-MM-DD)")
    parser.add_argument("-B", "--between", help="Fetch papers published BETWEEN these dates (YYYY-MM-DD,YYYY-MM-DD)")
    parser.add_argument("-S", "--sources", help="Comma-separated list of sources (arxiv,semanticscholar,crossref)")
    parser.add_argument("-F", "--format", choices=["pdf", "html", "epub", "docx", "latex", "json", "md"], help="Final output format")
    
    args = parser.parse_args()
    
    cfg = ConfigManager.load(args)

    Orchestrator(cfg).execute_pipeline()
