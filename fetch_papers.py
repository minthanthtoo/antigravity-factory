import arxiv
import os
import argparse
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename: str) -> str:
    """Sanitize the filename for safe storage."""
    # Remove special characters and replace spaces with underscores
    return re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')

def fetch_papers(query: str, limit: int, output_dir: str):
    """Search for papers on arXiv and download them as PDFs."""
    os.makedirs(output_dir, exist_ok=True)
    
    logging.info(f"🔎 Searching arXiv for: '{query}' (Limit: {limit})...")
    
    search = arxiv.Search(
        query=query,
        max_results=limit,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    client = arxiv.Client()
    
    downloaded_count = 0
    for result in client.results(search):
        paper_title = result.title
        sanitized_title = sanitize_filename(paper_title)
        filename = f"{sanitized_title}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        if os.path.exists(filepath):
            logging.info(f"⏭️ Skipping (Already exists): {filename}")
            continue
            
        logging.info(f"📥 Downloading: {paper_title}...")
        try:
            result.download_pdf(dirpath=output_dir, filename=filename)
            logging.info(f"✅ Saved to: {filepath}")
            downloaded_count += 1
        except Exception as e:
            logging.error(f"❌ Failed to download '{paper_title}': {e}")
            
    logging.info(f"🏁 Finished. Downloaded {downloaded_count} papers to '{output_dir}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search and download papers from arXiv.")
    parser.add_argument("--query", type=str, required=True, help="Search query (e.g., 'physics of agentic ai')")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of papers to download (default: 5)")
    parser.add_argument("--output", type=str, default="./papers", help="Directory to save papers (default: ./papers)")
    
    args = parser.parse_args()
    
    fetch_papers(args.query, args.limit, args.output)
