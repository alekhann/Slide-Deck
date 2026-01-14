# Quick Start Guide

## Setup Complete ✓

Your multi-agent research paper to slide deck generator with smart image matching is ready!

## Prerequisites

1. **Ollama installed** (for local LLM - no rate limits!)
   ```bash
   # Download from https://ollama.com/download
   # Or use: winget install Ollama.Ollama
   ```

2. **Pull the model**
   ```bash
   ollama pull llama3.2:3b
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Option 1: Process arXiv Paper (Recommended)
```bash
python main.py https://arxiv.org/abs/1512.01693
```

### Option 2: Process Local PDF
```bash
python main.py path/to/your/paper.pdf
```

### Option 3: Interactive Mode
```bash
python main.py
```
Then follow the prompts.

## Complete Workflow

For best results with figures and charts, use this workflow:

```bash
# 1. Run the main pipeline (generates text content)
python main.py https://arxiv.org/abs/YOUR_PAPER_ID

# 2. Extract figures, charts, and tables from PDF
python extract_figures.py papers/YOUR_PAPER_ID.pdf

# 3. Create final presentation with smart image matching
python create_final_pptx.py
```

## What You'll Get

### Generated Files in `output/` directory:

1. **[Paper_Title].pptx** - PowerPoint presentation with:
   - Professional title slide
   - Content slides with actual research data
   - Smart-matched figures, charts, and tables
   - Clean, readable formatting

2. **slide_blueprint.txt** - Complete text version:
   - All slide content
   - Bullet points with specific details
   - Verification report with metrics

### Extracted Files in `extracted_figures/` directory:

- High-quality figures from the paper
- Charts and tables
- Architecture diagrams
- Experimental results visualizations

## Configuration

### Switch Between LLM Providers

Edit `.env` file:

```bash
# For local Ollama (no rate limits, free)
LLM_PROVIDER=ollama

# For Groq (faster, but has rate limits)
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
```

### Customize Formatting

Edit `config.py`:
```python
p
python create_final_pptx.py

# 4. Open the result
start output/DARQN_Final_with_Figures.pptx
```

## Advanced Usage

### Regenerate PPTX with Different Images
```bash
# Edit smart_image_matcher.py to adjust relevance threshold
# Then regenerate:
python create_final_pptx.py
```

### View Metrics and Verification
```bash
# Check the blueprint file for verification report
type output/slide_blueprint.txt
```

### Extract More/Fewer Figures
```bash
# Edit extract_figures.py size thresholds:
# - Increase for fewer, larger figures
# - Decrease for more, smaller figures
python extract_figures.py papers/YOUR_PAPER.pdf
```

## Next Steps

1. ✅ Test with sample: `python main.py https://arxiv.org/abs/1512.01693`
2. ✅ Try your own paper
3. ✅ Review verification metrics
4. ✅ Customize for your needs

Enjoy creating research presentations! 🚀
