# Project Structure

## Core Files

### Entry Point
- `main.py` - Main entry point for the application

### Pipeline
- `pipeline.py` - Main orchestration and workflow
- `agents.py` - CrewAI agent definitions
- `tasks.py` - Task definitions for agents
- `config.py` - Configuration settings
- `.env` - Environment variables

### Utilities
- `utils.py` - Text extraction and processing utilities
- `arxiv_downloader.py` - Download papers from arXiv
- `pdf_image_extractor.py` - Extract images from PDFs

### Slide Generation
- `pptx_generator.py` - PowerPoint presentation generation
- `slide_organizer.py` - Organize slides in logical order
- `smart_figure_matcher.py` - Match figures to slides intelligently
- `smart_image_matcher.py` - Match images to slide content
- `hallucination_filter.py` - Verify facts against source

### Configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

## Documentation

### Quick Start
- `START_HERE.txt` - Quick start guide
- `SETUP.md` - Setup instructions
- `README.md` - Main project readme

### Reference
- `SIMPLE_CONFIG.md` - Configuration guide
- `CONTENT_QUALITY_FIXES.md` - Content quality improvements
- `TROUBLESHOOTING.md` - Common issues and solutions
- `ARCHITECTURE.md` - System architecture (technical)
- `IMPROVEMENTS.md` - Change log and improvements

## Directories

- `papers/` - Downloaded research papers
- `extracted_figures/` - Extracted figures from papers
- `extracted_images/` - Extracted images from papers
- `output/` - Generated presentations and blueprints
- `env/` - Python virtual environment
- `__pycache__/` - Python cache files

## File Count

**Core Files**: 14
**Documentation**: 8
**Total**: 22 files (clean and organized!)

## Usage

```bash
# Quick start
python main.py

# With specific paper
python main.py papers/your_paper.pdf

# With arXiv URL
python main.py https://arxiv.org/abs/1706.03762
```

## Configuration

Edit `.env`:
```env
MODEL=mistral
```

That's it! Simple and clean. 🚀
