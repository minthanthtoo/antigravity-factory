import arxiv
import os
import re
import logging

class ResearchEngine:
    """Handles autonomous paper acquisition from academic databases."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _sanitize(self, title: str) -> str:
        return re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')

    def search_and_download(self, query: str, limit: int = 5):
        """Standard high-level entry point for paper acquisition."""
        logging.info(f"🔎 Research Engine: Searching for '{query}'...")
        
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        client = arxiv.Client()
        count = 0
        for result in client.results(search):
            filename = f"{self._sanitize(result.title)}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            if not os.path.exists(filepath):
                logging.info(f"📥 Downloading: {result.title}...")
                result.download_pdf(dirpath=self.output_dir, filename=filename)
                count += 1
            else:
                logging.info(f"⏭️ Using cached version: {filename}")
        
        return count
