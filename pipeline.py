"""Main pipeline orchestration for research paper to slide deck generation."""
from crewai import Crew, Process
from utils import (
    extract_text_from_pdf, clean_text, identify_sections,
    extract_figures_and_tables, save_output
)
from tasks import (
    create_ingestion_task, create_summarization_task,
    create_structuring_task, create_visualization_task,
    create_compression_task, create_verification_task,
    create_compilation_task
)
from agents import (
    ingestion_agent, summarization_agent, structuring_agent,
    visualization_agent, compression_agent, verification_agent,
    compilation_agent
)
from arxiv_downloader import download_arxiv_paper, get_arxiv_metadata
from pptx_generator import generate_pptx_from_blueprint
import config
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class ResearchPaperPipeline:
    """Main pipeline for converting research papers to slide decks."""
    
    def __init__(self, paper_path: str, target_slides: int = None, style: str = "concise", 
                 is_arxiv: bool = False):
        self.paper_path = paper_path
        self.target_slides = target_slides
        self.style = style
        self.is_arxiv = is_arxiv
        self.paper_text = None
        self.sections = None
        self.figures = None
        self.paper_title = "Research Paper"
        self.paper_metadata = None
        
    def run(self):
        """Execute the full pipeline."""
        console.print("\n[bold cyan]🚀 Starting Research Paper → Slide Deck Pipeline[/bold cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 0: Download from arXiv if needed
            if self.is_arxiv:
                task0 = progress.add_task("📥 Downloading from arXiv...", total=None)
                arxiv_id = self.paper_path  # Save original arXiv ID
                self.paper_path = download_arxiv_paper(arxiv_id)
                self.paper_metadata = get_arxiv_metadata(arxiv_id)  # Use arXiv ID, not file path
                self.paper_title = self.paper_metadata['title']
                progress.update(task0, completed=True)
                console.print(f"[green]✓[/green] Downloaded: {self.paper_title}\n")
            
            # Step 1: Ingestion
            task1 = progress.add_task("📄 Ingesting paper...", total=None)
            self.paper_text = self._ingest_paper()
            progress.update(task1, completed=True)
            console.print("[green]✓[/green] Paper ingested successfully\n")
            
            # Step 2: Section identification
            task2 = progress.add_task("📑 Identifying sections...", total=None)
            self.sections = identify_sections(self.paper_text)
            self.figures = extract_figures_and_tables(self.paper_text)
            progress.update(task2, completed=True)
            console.print(f"[green]✓[/green] Found {len(self.sections)} sections and {len(self.figures)} figures/tables\n")
            
            # Step 3: Run agent crew
            task3 = progress.add_task("🤖 Running agent crew...", total=None)
            result = self._run_agent_crew()
            progress.update(task3, completed=True)
            console.print("[green]✓[/green] Agent processing complete\n")
            
            # Step 4: Save outputs
            task4 = progress.add_task("💾 Saving outputs...", total=None)
            self._save_results(result)
            progress.update(task4, completed=True)
            console.print("[green]✓[/green] Results saved to output directory\n")
            
            # Step 5: Generate PowerPoint
            task5 = progress.add_task("📊 Generating PowerPoint...", total=None)
            pptx_path = self._generate_pptx(result)
            progress.update(task5, completed=True)
            console.print(f"[green]✓[/green] PowerPoint generated: {pptx_path}\n")
        
        console.print("[bold green]✨ Pipeline completed successfully![/bold green]\n")
        return result
    
    def _ingest_paper(self):
        """Ingest and clean paper text."""
        if self.paper_path.endswith('.pdf'):
            text = extract_text_from_pdf(self.paper_path)
        else:
            with open(self.paper_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        return clean_text(text)
    
    def _run_agent_crew(self):
        """Run the CrewAI agent pipeline."""
        
        # Create tasks
        tasks = [
            create_summarization_task(self.sections),
            create_structuring_task(self.sections),
            create_visualization_task(
                {'text': self.paper_text, 'figures': self.figures},
                self.sections
            ),
            create_compression_task(self.sections),
            create_verification_task(self.sections, self.paper_text),
            create_compilation_task(self.sections, self.figures, self.paper_text)
        ]
        
        # Create crew
        crew = Crew(
            agents=[
                summarization_agent,
                structuring_agent,
                visualization_agent,
                compression_agent,
                verification_agent,
                compilation_agent
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute
        result = crew.kickoff()
        return result
    
    def _save_results(self, result):
        """Save pipeline results to files."""
        # Save main result
        save_output(config.SLIDES_OUTPUT, str(result))
        
        console.print(f"\n[bold]Output files:[/bold]")
        console.print(f"  • {config.OUTPUT_DIR}/{config.SLIDES_OUTPUT}")
        console.print(f"  • Check the output directory for all generated files\n")
    
    def _generate_pptx(self, result):
        """Generate PowerPoint presentation with unique filename and extracted images."""
        import time
        import re
        from pdf_image_extractor import get_relevant_images
        
        # Extract images from PDF
        extracted_images = []
        try:
            if self.paper_path and os.path.exists(self.paper_path):
                console.print("[cyan]Extracting images from PDF...[/cyan]")
                extracted_images = get_relevant_images(self.paper_path, max_images=10)
                console.print(f"[green]✓[/green] Extracted {len(extracted_images)} images\n")
        except Exception as e:
            console.print(f"[yellow]Could not extract images: {e}[/yellow]")
        
        # Create filename from paper title
        if self.paper_title and self.paper_title != "Research Paper":
            # Clean title for filename
            clean_title = re.sub(r'[^\w\s-]', '', self.paper_title)
            clean_title = re.sub(r'[-\s]+', '_', clean_title)
            clean_title = clean_title[:50]  # Limit length
            pptx_filename = f"{clean_title}.pptx"
        else:
            # Use timestamp if no title
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            pptx_filename = f"presentation_{timestamp}.pptx"
        
        pptx_path = os.path.join(config.OUTPUT_DIR, pptx_filename)
        
        # If file exists, add number suffix
        if os.path.exists(pptx_path):
            base_name = pptx_filename.replace('.pptx', '')
            counter = 1
            while os.path.exists(pptx_path):
                pptx_filename = f"{base_name}_{counter}.pptx"
                pptx_path = os.path.join(config.OUTPUT_DIR, pptx_filename)
                counter += 1
        
        try:
            # Generate PPTX with extracted images
            generate_pptx_from_blueprint(str(result), pptx_path, self.paper_title, extracted_images)
            console.print(f"[green]Generated:[/green] {pptx_filename}")
        except Exception as e:
            console.print(f"[red]Error generating PowerPoint: {e}[/red]")
            raise
        
        return pptx_path

def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        console.print("[red]Usage: python pipeline.py <path_to_paper.pdf>[/red]")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    pipeline = ResearchPaperPipeline(paper_path)
    pipeline.run()

if __name__ == "__main__":
    main()
