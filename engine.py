try:
    from fetcher import ResearchEngine
except ImportError:
    ResearchEngine = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TokenCounter:
    """Fix Level 8.3: Cost Safety."""
    def __init__(self, budget: int = 1000000):
        self.total_tokens = 0
        self.budget = budget

    def add(self, text: str):
        count = len(text) // 4
        self.total_tokens += count
        if self.total_tokens > self.budget:
            raise Exception(f"❌ Token Budget Exceeded ({self.total_tokens} > {self.budget}).")
        return count

class Orchestrator:
    def __init__(self, corpus_path: str, output_path: str, user_config: Dict[str, str] = {}):
        self.corpus_path = corpus_path
        self.output_path = output_path
        self.user_config = user_config
        self.prompts = self._load_prompts()
        self.counter = TokenCounter(budget=user_config.get("TOKEN_BUDGET", 5000000))
        
        # Protocols Integration
        self.master_ref = ""
        v2_path = os.path.join(os.path.dirname(__file__), "protocols.md")
        if os.path.exists(v2_path):
            with open(v2_path, 'r', encoding='utf-8') as f:
                self.master_ref = f.read()
                
        self._validate_environment()

    def _validate_environment(self):
        has_key = "GOOGLE_API_KEY" in os.environ or "OPENAI_API_KEY" in os.environ
        if not has_key:
            if self.user_config.get("STRICT_MODE", False):
                raise Exception("❌ Environment Error: No API Key found.")
            logging.warning("⚠️ No API Key found. Running in MOCK MODE.")
        
        if ResearchEngine is None and "SEARCH_QUERY" in self.user_config:
            logging.warning("⚠️ 'research_engine' module not found. Search functionality will be disabled.")

    def _acquire_papers(self, query: str, limit: int = 5):
        """Trigger the modular Research Engine."""
        if ResearchEngine is None:
            logging.error("❌ Cannot acquire papers: ResearchEngine module missing.")
            return

        engine = ResearchEngine(self.corpus_path)
        engine.search_and_download(query, limit)

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

    def _call_llm_with_retry(self, system_prompt: str, user_content: str, max_retries: int = 3) -> str:
        # Enforce global protocols from constitution.md
        full_system_prompt = f"{self.master_ref}\n\n### SPECIFIC AGENT ROLE:\n{system_prompt}"
        self.counter.add(full_system_prompt + user_content)
        attempt = 0
        while attempt < max_retries:
            try:
                if "GOOGLE_API_KEY" in os.environ:
                    response = self._call_real_gemini(full_system_prompt, user_content)
                    self.counter.add(response)
                    return response
                else:
                    return self._mock_llm_response(full_system_prompt)
            except Exception as e:
                attempt += 1
                wait_time = 2 ** attempt
                logging.error(f"API Error: {e}. Retry {attempt}/{max_retries}...")
                time.sleep(wait_time)
        return "Critical API Failure"

    def _call_real_gemini(self, system_prompt: str, user_content: str) -> str:
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(f"SYSTEM: {system_prompt}\nUSER: {user_content}")
            return response.text
        except ImportError:
            if "GOOGLE_API_KEY" in os.environ: raise Exception("❌ Library missing.")
            return self._mock_llm_response(system_prompt)

    def _mock_llm_response(self, system_prompt: str) -> str:
        time.sleep(0.1)
        if "Architect" in system_prompt: return "<synthesis_matrix>X: [1]</synthesis_matrix>## Outline\n- Introduction"
        if "Writer" in system_prompt: return "# Chapter Content\nDraft using [1]..."
        if "Critic" in system_prompt: return "Status: PASS"
        return "Summary preserving [1]."

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
        logging.info("🚀 Starting Pipeline...")
        
        # Phase 0: Acquisition
        if "SEARCH_QUERY" in self.user_config:
            self._acquire_papers(self.user_config["SEARCH_QUERY"], int(self.user_config.get("PAPER_LIMIT", 5)))

        docs = glob.glob(os.path.join(self.corpus_path, "*.pdf")) + glob.glob(os.path.join(self.corpus_path, "*.md"))
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

            logging.info(f"✍️ Drafting {ch}...")
            base_p = self._render_prompt(self.prompts["writer"], {"CHAPTER_TITLE": ch, "BLUEPRINT": blueprint, "PREVIOUS_CHAPTER_SUMMARY": prev_summ})
            
            ok, retries, hist = False, 0, [] 
            while not ok and retries < 3:
                draft = self._call_llm(base_p, f"Draft {ch}")
                if not self._validate_mermaid(draft): critique = "FAIL: Visuals."
                else: 
                    critic_p = self._render_prompt(self.prompts["critic"], {"PREVIOUS_CRITIQUES": "\n".join(hist)})
                    critique = self._call_llm(critic_p, draft)
                hist.append(critique)
                if "Status: PASS" in critique: ok = True
                else: 
                    retries += 1
                    base_p += f"\n\nLATEST FEEDBACK: {critique}"
            
            if ok:
                self.save_chapter(ch, self._lint_latex_safety(draft))
                manifest["chapters"][ch] = "READY"
                s_p = self._render_prompt(self.prompts["summarizer"], {"CHAPTER_CONTENT": draft})
                prev_summ = self._call_llm(s_p, "Summarize.")
            else:
                manifest["status"] = "BROKEN"
                break

        if manifest["status"] == "IN_PROGRESS": manifest["status"] = "READY"
        
        if manifest["status"] == "READY":
            self.trigger_build_pipeline(manifest)
        else:
            logging.error("🚫 ABORTED: Incomplete Manifest.")

    def trigger_build_pipeline(self, manifest: Dict):
        """Fix Level 6.2 & 9.4: Pipelining."""
        master_file = "the_physics_of_agentic_ai_full.md"
        logging.info(f"🧵 Stitching master file: {master_file}...")
        try:
            with open(master_file, 'w', encoding='utf-8') as master:
                for ch in manifest["chapters"].keys():
                    fn = f"{ch.lower().replace(' ', '_')}.md"
                    path = os.path.join(self.output_path, fn)
                    if os.path.exists(path):
                        with open(path, 'r', encoding='utf-8') as f:
                            master.write(f.read() + "\n\n")
            
            if not os.path.exists("refs.bib"):
                with open("refs.bib", 'w') as f: f.write("@misc{placeholder, title={Placeholder}}")

            script = os.path.join(os.path.dirname(__file__), "typeset.sh")
            if os.path.exists(script):
                subprocess.run(["bash", script])
                logging.info("📚 PDF/HTML Generation finished.")
        except Exception as e:
            logging.error(f"❌ Mastering failed: {e}")

    def save_chapter(self, title: str, content: str):
        fn = f"{title.lower().replace(' ', '_')}.md"
        os.makedirs(self.output_path, exist_ok=True)
        with open(os.path.join(self.output_path, fn), 'w', encoding='utf-8') as f: f.write(content)

if __name__ == "__main__":
    cfg = {"CORPUS_PATH": "./papers", "OUTPUT_PATH": "./book_out"}
    Orchestrator(cfg["CORPUS_PATH"], cfg["OUTPUT_PATH"], cfg).execute_pipeline()
