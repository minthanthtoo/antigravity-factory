import os
import arxiv
import logging
from typing import List

class ResearchEngine:
    """Fix Level 9.1: Autonomous Acquisition."""
    def __init__(self, download_dir: str = "./papers"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        logging.basicConfig(level=logging.INFO)

    def search_and_download(self, query: str, limit: int = 5):
        logging.info(f"🔍 Searching arXiv for: {query}")
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.Relevance
        )

        for result in search.results():
            filename = f"{result.get_short_id()}.pdf"
            path = os.path.join(self.download_dir, filename)
            if os.path.exists(path):
                logging.info(f"⏩ skipping {filename} (exists)")
                continue
            
            logging.info(f"📥 Downloading {result.title}...")
            result.download_pdf(dirpath=self.download_dir, filename=filename)

if __name__ == "__main__":
    engine = ResearchEngine()
    engine.search_and_download("agentic ai architecture", limit=3)
