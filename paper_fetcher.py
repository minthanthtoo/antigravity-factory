import os
import arxiv
import logging
import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class ResearchPaper:
    id: str
    title: str
    authors: List[str]
    summary: str
    url: str
    pdf_url: Optional[str] = None
    source: str = "unknown"

class BaseProvider:
    def search(self, query: str, limit: int = 5, start_date: str = None, end_date: str = None) -> List[ResearchPaper]:
        raise NotImplementedError

class ArxivProvider(BaseProvider):
    def search(self, query: str, limit: int = 5, start_date: str = None, end_date: str = None) -> List[ResearchPaper]:
        full_query = query
        if start_date or end_date:
            date_start = start_date.replace("-", "") + "0000" if start_date else "000001010000"
            date_end = end_date.replace("-", "") + "2359" if end_date else "999912312359"
            full_query = f"({query}) AND submittedDate:[{date_start} TO {date_end}]"

        search = arxiv.Search(
            query=full_query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.SubmittedDate if (start_date or end_date) else arxiv.SortCriterion.Relevance
        )

        papers = []
        for res in search.results():
            papers.append(ResearchPaper(
                id=res.get_short_id(),
                title=res.title,
                authors=[a.name for a in res.authors],
                summary=res.summary,
                url=res.entry_id,
                pdf_url=res.pdf_url,
                source="arxiv"
            ))
        return papers

class SemanticScholarProvider(BaseProvider):
    def search(self, query: str, limit: int = 5, start_date: str = None, end_date: str = None) -> List[ResearchPaper]:
        # Semantic Scholar API: https://api.semanticscholar.org/graph/v1/paper/search
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,abstract,url,openAccessPdf"
        }
        # Date filtering in Semantic Scholar is via year range, we'll approximate
        if start_date or end_date:
            year_start = start_date.split("-")[0] if start_date else "1900"
            year_end = end_date.split("-")[0] if end_date else "2025"
            params["year"] = f"{year_start}-{year_end}"

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get("data", []):
                authors = [a.get("name") for a in item.get("authors", [])]
                pdf_url = item.get("openAccessPdf", {}).get("url") if item.get("openAccessPdf") else None
                papers.append(ResearchPaper(
                    id=item.get("paperId"),
                    title=item.get("title"),
                    authors=authors,
                    summary=item.get("abstract") or "No abstract available.",
                    url=item.get("url"),
                    pdf_url=pdf_url,
                    source="semanticscholar"
                ))
            return papers
        except Exception as e:
            logging.error(f"Semantic Scholar Search Failed: {e}")
            return []

class CrossrefProvider(BaseProvider):
    def search(self, query: str, limit: int = 5, start_date: str = None, end_date: str = None) -> List[ResearchPaper]:
        # Crossref API: https://api.crossref.org/works
        url = "https://api.crossref.org/works"
        params = {
            "query": query,
            "rows": limit,
            "select": "DOI,title,author,abstract,URL,link"
        }
        # Date filtering in Crossref
        if start_date:
            params["filter"] = f"from-pub-date:{start_date}"
        if end_date:
             params["filter"] = params.get("filter", "") + f",until-pub-date:{end_date}"

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get("message", {}).get("items", []):
                title = item.get("title", ["Unknown"])[0]
                authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get("author", [])]
                doi = item.get("DOI")
                pdf_url = None
                # Attempt to find a PDF link
                for link in item.get("link", []):
                    if link.get("content-type") == "application/pdf":
                        pdf_url = link.get("URL")
                        break
                
                paper = ResearchPaper(
                    id=doi,
                    title=title,
                    authors=authors,
                    summary=item.get("abstract") or "No abstract available.",
                    url=item.get("URL"),
                    pdf_url=pdf_url,
                    source="crossref"
                )
                papers.append(paper)
            return papers
        except Exception as e:
            logging.error(f"Crossref Search Failed: {e}")
            return []

class ResearchEngine:
    def __init__(self, download_dir: str = "./papers"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.providers = {
            "arxiv": ArxivProvider(),
            "semanticscholar": SemanticScholarProvider(),
            "crossref": CrossrefProvider()
        }

    def search_and_download(self, query: str, limit: int = 5, start_date: str = None, end_date: str = None, fetch_mode: str = "fulltext", auto_confirm: bool = False, sources: List[str] = ["arxiv"]):
        all_papers = []
        for src in sources:
            if src in self.providers:
                logging.info(f"Searching {src} for: {query}...")
                all_papers.extend(self.providers[src].search(query, limit, start_date, end_date))
        
        # Deduplicate
        seen_ids = set()
        unique_papers = []
        for p in all_papers:
            if p.id not in seen_ids:
                unique_papers.append(p)
                seen_ids.add(p.id)

        count = len(unique_papers)
        logging.info(f"Found {count} unique papers across {len(sources)} sources.")

        if count == 0:
            return

        selected_papers = unique_papers[:limit]
        
        if not auto_confirm:
            try:
                ans = input(f"Proceed to download {len(selected_papers)} papers (from {count} found) in '{fetch_mode}' mode? [y/N]: ").lower()
                if ans != 'y':
                    logging.info("Download cancelled by user.")
                    return
            except EOFError:
                logging.warning("Non-interactive environment. Proceeding.")

        self._save_catalog(selected_papers)

        for paper in selected_papers:
            safe_id = paper.id.replace("/", "_").replace(":", "_") # Safe filename
            if fetch_mode == "fulltext" and paper.pdf_url:
                filename = f"{safe_id}.pdf"
                path = os.path.join(self.download_dir, filename)
                
                # Auto-Resume Check: File must exist and be valid (non-empty)
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    logging.info(f"[Resume] Paper {safe_id} already exists (PDF). Skipping.")
                    continue
                
                logging.info(f"Downloading PDF from {paper.source}: {paper.title}...")
                try:
                    # Stream download for memory efficiency
                    res = requests.get(paper.pdf_url, stream=True, timeout=30)
                    res.raise_for_status()
                    with open(path, 'wb') as f:
                        for chunk in res.iter_content(chunk_size=8192):
                            if chunk: f.write(chunk)
                except Exception as e:
                    logging.error(f"Failed to download PDF for {paper.id}: {e}")
                    # Fallback to abstract if PDF fails
                    self._save_abstract(paper)
            else:
                self._save_abstract(paper)

    def _save_catalog(self, papers: List[ResearchPaper]):
        catalog_path = os.path.join(self.download_dir, "research_catalog.json")
        catalog_data = [asdict(p) for p in papers]
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2)
        logging.info(f"Structured catalog saved to: {catalog_path}")

    def _save_abstract(self, paper: ResearchPaper):
        safe_id = paper.id.replace("/", "_").replace(":", "_")
        filename = f"{safe_id}.md"
        path = os.path.join(self.download_dir, filename)
        
        # Auto-Resume Check: Abstract exists and is non-empty
        if os.path.exists(path) and os.path.getsize(path) > 0:
            logging.info(f"[Resume] Paper {safe_id} already exists (Abstract). Skipping.")
            return

        logging.info(f"Saving Abstract from {paper.source}: {paper.title}...")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# {paper.title}\n\n")
            f.write(f"**Source**: {paper.source}\n")
            f.write(f"**Authors**: {', '.join(paper.authors)}\n\n")
            f.write(f"**URL**: {paper.url}\n\n")
            f.write(f"## Abstract\n{paper.summary}\n")

if __name__ == "__main__":
    engine = ResearchEngine()
    engine.search_and_download("agentic ai architecture", limit=3, sources=["arxiv", "semanticscholar"])
