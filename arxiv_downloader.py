"""Download papers from arXiv."""
import arxiv
import os
from rich.console import Console

console = Console()

def download_arxiv_paper(arxiv_id_or_url: str, download_dir: str = "papers") -> str:
    """
    Download a paper from arXiv.
    
    Args:
        arxiv_id_or_url: arXiv ID (e.g., "2301.07041") or full URL
        download_dir: Directory to save the paper
        
    Returns:
        Path to the downloaded PDF file
    """
    # Extract arXiv ID from URL if needed
    if "arxiv.org" in arxiv_id_or_url:
        # Extract ID from URL like https://arxiv.org/abs/2301.07041
        arxiv_id = arxiv_id_or_url.split("/")[-1].replace(".pdf", "")
    else:
        arxiv_id = arxiv_id_or_url
    
    console.print(f"[cyan]Downloading arXiv paper: {arxiv_id}[/cyan]")
    
    # Create download directory
    os.makedirs(download_dir, exist_ok=True)
    
    try:
        # Search for the paper
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        
        console.print(f"[green]Found:[/green] {paper.title}")
        console.print(f"[green]Authors:[/green] {', '.join([a.name for a in paper.authors[:3]])}...")
        
        # Download the PDF
        pdf_path = paper.download_pdf(dirpath=download_dir, filename=f"{arxiv_id}.pdf")
        
        console.print(f"[green]✓ Downloaded to:[/green] {pdf_path}\n")
        return pdf_path
        
    except Exception as e:
        console.print(f"[red]Error downloading paper: {e}[/red]")
        raise

def get_arxiv_metadata(arxiv_id_or_url: str) -> dict:
    """Get metadata for an arXiv paper without downloading."""
    if "arxiv.org" in arxiv_id_or_url:
        arxiv_id = arxiv_id_or_url.split("/")[-1].replace(".pdf", "")
    else:
        arxiv_id = arxiv_id_or_url
    
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(search.results())
    
    return {
        "title": paper.title,
        "authors": [a.name for a in paper.authors],
        "abstract": paper.summary,
        "published": paper.published,
        "pdf_url": paper.pdf_url,
        "categories": paper.categories
    }
