"""Simple entry point for the research paper to slide deck generator."""
import sys
from pipeline import ResearchPaperPipeline
from rich.console import Console

console = Console()

def main():
    """Main entry point with user-friendly interface."""
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  Research Paper → Slide Deck Generator[/bold cyan]")
    console.print("[bold cyan]  Supports: PDF, TXT, arXiv URLs[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════[/bold cyan]\n")
    
    # Get paper path
    if len(sys.argv) > 1:
        paper_input = sys.argv[1]
    else:
        console.print("[yellow]Examples:[/yellow]")
        console.print("  • Local PDF: paper.pdf")
        console.print("  • arXiv URL: https://arxiv.org/abs/2301.07041")
        console.print("  • arXiv ID: 2301.07041\n")
        paper_input = input("Enter paper path, arXiv URL, or arXiv ID: ").strip()
    
    # Detect if it's arXiv
    is_arxiv = "arxiv" in paper_input.lower() or (
        len(paper_input.split('.')) == 2 and paper_input.replace('.', '').isdigit()
    )
    
    # Optional parameters
    target_slides = input("Target number of slides (press Enter to skip): ").strip()
    target_slides = int(target_slides) if target_slides else None
    
    style = input("Presentation style [concise/detailed/teaching] (default: concise): ").strip()
    style = style if style in ['concise', 'detailed', 'teaching'] else 'concise'
    
    # Run pipeline
    try:
        pipeline = ResearchPaperPipeline(
            paper_path=paper_input,
            target_slides=target_slides,
            style=style,
            is_arxiv=is_arxiv
        )
        result = pipeline.run()
        
        console.print("\n[bold green]✨ Success! Generated files in 'output' directory:[/bold green]")
        console.print("  📄 slide_blueprint.txt (detailed text format)")
        console.print("  📊 presentation.pptx (PowerPoint slides)")
        console.print("\n[cyan]Tip: Close any open PowerPoint files before running again![/cyan]\n")
        
    except FileNotFoundError:
        console.print(f"\n[bold red]Error: File not found: {paper_input}[/bold red]\n")
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        raise

if __name__ == "__main__":
    main()
