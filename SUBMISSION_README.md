# Research Paper to Slide Deck Generator - Submission Package

## Package Contents

This ZIP file contains the complete source code for the Research Paper to Slide Deck Generator, excluding the virtual environment and generated files to keep the package size small.

### Included Files

**Core Source Code** (14 files):
- `main.py` - Entry point
- `pipeline.py` - Main orchestration
- `agents.py` - Agent definitions
- `tasks.py` - Task definitions
- `config.py` - Configuration
- `.env` - Environment variables
- `utils.py` - Utilities
- `arxiv_downloader.py` - ArXiv downloads
- `pdf_image_extractor.py` - Image extraction
- `pptx_generator.py` - PowerPoint generation
- `slide_organizer.py` - Slide organization
- `smart_figure_matcher.py` - Figure matching
- `smart_image_matcher.py` - Image matching
- `hallucination_filter.py` - Fact verification

**Documentation** (8 files):
- `README.md` - Main readme
- `START_HERE.txt` - Quick start guide
- `SETUP.md` - Setup instructions
- `SIMPLE_CONFIG.md` - Configuration guide
- `CONTENT_QUALITY_FIXES.md` - Content improvements
- `TROUBLESHOOTING.md` - Troubleshooting
- `ARCHITECTURE.md` - System architecture
- `IMPROVEMENTS.md` - Change log

**Configuration**:
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

### Excluded (Can be Regenerated)

- `env/` - Virtual environment (recreate with setup instructions)
- `__pycache__/` - Python cache files
- `output/` - Generated presentations
- `papers/` - Downloaded papers
- `extracted_figures/` - Extracted figures
- `extracted_images/` - Extracted images

## Setup Instructions

### 1. Extract the ZIP file
```bash
unzip research_paper_to_slides_submission.zip
cd research_paper_to_slides_submission
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Ollama and Model
```bash
# Install Ollama from https://ollama.ai
# Then pull the model:
ollama pull mistral
```

### 5. Run the Application
```bash
python main.py
```

## Quick Start

After setup, simply run:
```bash
python main.py
```

The system will:
1. Prompt for a paper (PDF path or arXiv URL)
2. Process the paper (1-3 minutes)
3. Generate a PowerPoint presentation
4. Save to `output/` folder

## Configuration

Edit `.env` to change the model:
```env
MODEL=mistral          # Fastest (1-3 min)
MODEL=qwen2.5:7b       # Better quality (5-10 min)
MODEL=qwen2.5:14b      # High quality (10-15 min)
```

## Features

✅ Paper title as first slide
✅ Actual informative content (not "mention this")
✅ Specific numbers and details
✅ Clean formatting (no labels)
✅ Relevant images only
✅ Logical slide structure
✅ No timeout errors

## System Requirements

- Python 3.8+
- 4GB+ RAM (for Mistral model)
- Ollama installed
- Windows/Linux/Mac

## Package Size

- **Compressed**: ~0.1 MB
- **After extraction**: ~0.5 MB
- **With virtual environment**: ~500 MB (after pip install)

## Support

See documentation files:
- `START_HERE.txt` - Quick start
- `SETUP.md` - Detailed setup
- `TROUBLESHOOTING.md` - Common issues

## License

[Your License Here]

## Contact

[Your Contact Information]

---

**Note**: This package excludes the virtual environment to keep the size small. Follow the setup instructions above to recreate the environment.
