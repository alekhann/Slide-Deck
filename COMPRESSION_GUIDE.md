# Compression Guide for Submission

## Problem
The project folder is large (~500 MB+) due to the virtual environment (`env/` folder).

## Solution
Use the provided script to create a clean submission package that excludes the virtual environment.

## How to Create Submission Package

### Method 1: Using the Script (Recommended)

```bash
python create_submission.py
```

This will create `research_paper_to_slides_submission.zip` (~0.1 MB)

### Method 2: Manual ZIP (Windows)

1. Select these files/folders:
   - All `.py` files
   - All `.md` files
   - `.env`
   - `.gitignore`
   - `requirements.txt`
   - `START_HERE.txt`

2. Right-click → Send to → Compressed (zipped) folder

3. **DO NOT include**:
   - `env/` folder
   - `__pycache__/` folder
   - `output/` folder
   - `papers/` folder
   - `extracted_figures/` folder
   - `extracted_images/` folder

### Method 3: Using PowerShell

```powershell
# Compress without env folder
Compress-Archive -Path *.py,*.md,*.txt,.env,.gitignore,requirements.txt -DestinationPath submission.zip
```

### Method 4: Using Command Line (Linux/Mac)

```bash
# Create ZIP excluding env and cache
zip -r submission.zip . -x "env/*" "__pycache__/*" "*.pyc" "output/*" "papers/*" "extracted_*/*"
```

## What Gets Included

✅ **Source Code** (14 files):
- main.py, pipeline.py, agents.py, tasks.py, config.py
- utils.py, arxiv_downloader.py, pdf_image_extractor.py
- pptx_generator.py, slide_organizer.py
- smart_figure_matcher.py, smart_image_matcher.py
- hallucination_filter.py, .env

✅ **Documentation** (8 files):
- README.md, START_HERE.txt, SETUP.md
- SIMPLE_CONFIG.md, CONTENT_QUALITY_FIXES.md
- TROUBLESHOOTING.md, ARCHITECTURE.md, IMPROVEMENTS.md

✅ **Configuration**:
- requirements.txt
- .gitignore

## What Gets Excluded

❌ **Large Folders**:
- `env/` - Virtual environment (~500 MB)
- `__pycache__/` - Python cache
- `output/` - Generated files
- `papers/` - Downloaded papers
- `extracted_figures/` - Extracted images
- `extracted_images/` - Extracted images

## Size Comparison

| Package | Size |
|---------|------|
| Full project (with env) | ~500 MB |
| Submission package | ~0.1 MB |
| **Reduction** | **99.98%** |

## Recipient Instructions

Include these instructions for the recipient:

```markdown
## Setup Instructions

1. Extract the ZIP file
2. Create virtual environment:
   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   source env/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Ollama and model:
   ```bash
   ollama pull mistral
   ```
5. Run:
   ```bash
   python main.py
   ```
```

## Verification

After creating the ZIP, verify it contains:

```bash
# List contents (Windows PowerShell)
Expand-Archive -Path submission.zip -DestinationPath temp_check
Get-ChildItem temp_check -Recurse
Remove-Item temp_check -Recurse

# List contents (Linux/Mac)
unzip -l submission.zip
```

Should show:
- ✓ All .py files
- ✓ All .md files
- ✓ requirements.txt
- ✓ .env
- ✗ No env/ folder
- ✗ No __pycache__/ folder

## Automated Script Features

The `create_submission.py` script:

✅ Automatically excludes virtual environment
✅ Excludes cache files
✅ Excludes generated outputs
✅ Creates clean ZIP file
✅ Shows file size
✅ Lists all included files
✅ Provides setup instructions

## Tips

1. **Always use the script** - It ensures consistency
2. **Check the size** - Should be < 1 MB
3. **Test extraction** - Extract and verify files
4. **Include README** - Add setup instructions
5. **Version control** - Use git to track changes

## Troubleshooting

### ZIP is too large (> 10 MB)
- Check if `env/` folder is included
- Check if `papers/` folder is included
- Use the script instead of manual compression

### Missing files after extraction
- Verify all .py files are included
- Check requirements.txt is present
- Ensure .env file is included

### Can't run after extraction
- Recipient needs to create virtual environment
- Recipient needs to install dependencies
- Recipient needs to install Ollama

## Summary

**Use this command**:
```bash
python create_submission.py
```

**Result**:
- Clean ZIP file (~0.1 MB)
- All source code included
- No virtual environment
- Ready for submission

**Recipient can recreate everything with**:
```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
ollama pull mistral
python main.py
```

Simple and efficient! 🚀
