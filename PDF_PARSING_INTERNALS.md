# PDF and arXiv Parsing Internals

## Overview

This document provides a detailed explanation of how PDFs and arXiv URLs are parsed internally in the pipeline, including the complete flow from input to structured data.

---

## Table of Contents

1. [Input Detection and Routing](#input-detection-and-routing)
2. [arXiv URL/ID Processing](#arxiv-urlid-processing)
3. [PDF Text Extraction](#pdf-text-extraction)
4. [PDF Image Extraction](#pdf-image-extraction)
5. [Text Cleaning and Normalization](#text-cleaning-and-normalization)
6. [Section Identification](#section-identification)
7. [Figure and Table Extraction](#figure-and-table-extraction)
8. [Complete Flow Diagram](#complete-flow-diagram)
9. [Error Handling](#error-handling)

---

## 1. Input Detection and Routing

### Entry Point: `main.py`

```python
def main():
    # Get input from user or command line
    paper_input = sys.argv[1] if len(sys.argv) > 1 else input("Enter paper path...")
    
    # Detect input type
    is_arxiv = "arxiv" in paper_input.lower() or (
        len(paper_input.split('.')) == 2 and 
        paper_input.replace('.', '').isdigit()
    )
```

**Detection Logic**:

| Input Type | Example | Detection Method |
|------------|---------|------------------|
| arXiv URL | `https://arxiv.org/abs/1706.03762` | Contains "arxiv" |
| arXiv ID | `1706.03762` | Format: `XXXX.XXXXX` (digits with dot) |
| Local PDF | `paper.pdf` | Ends with `.pdf` |
| Text File | `paper.txt` | Ends with `.txt` |

**Routing Decision**:
```python
if is_arxiv:
    # Route to arXiv downloader
    pipeline = ResearchPaperPipeline(paper_input, is_arxiv=True)
else:
    # Route to direct file processing
    pipeline = ResearchPaperPipeline(paper_input, is_arxiv=False)
```

---

## 2. arXiv URL/ID Processing

### Module: `arxiv_downloader.py`

#### Step 2.1: ID Extraction

```python
def download_arxiv_paper(arxiv_id_or_url: str) -> str:
    # Extract ID from URL if needed
    if "arxiv.org" in arxiv_id_or_url:
        # URL: https://arxiv.org/abs/1706.03762
        # Extract: 1706.03762
        arxiv_id = arxiv_id_or_url.split("/")[-1].replace(".pdf", "")
    else:
        # Already an ID: 1706.03762
        arxiv_id = arxiv_id_or_url
```

**URL Parsing Examples**:
- `https://arxiv.org/abs/1706.03762` → `1706.03762`
- `https://arxiv.org/pdf/1706.03762.pdf` → `1706.03762`
- `1706.03762` → `1706.03762` (no change)

#### Step 2.2: Paper Search

```python
# Use arxiv Python library
search = arxiv.Search(id_list=[arxiv_id])
paper = next(search.results())
```

**API Call**:
- Endpoint: arXiv API
- Method: Search by ID
- Returns: Paper metadata object

#### Step 2.3: Metadata Extraction

```python
metadata = {
    "title": paper.title,
    "authors": [a.name for a in paper.authors],
    "abstract": paper.summary,
    "published": paper.published,
    "pdf_url": paper.pdf_url,
    "categories": paper.categories
}
```

**Metadata Structure**:
```json
{
    "title": "Attention Is All You Need",
    "authors": ["Ashish Vaswani", "Noam Shazeer", ...],
    "abstract": "The dominant sequence transduction models...",
    "published": "2017-06-12",
    "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
    "categories": ["cs.CL", "cs.LG"]
}
```

#### Step 2.4: PDF Download

```python
# Download to papers/ directory
pdf_path = paper.download_pdf(
    dirpath="papers",
    filename=f"{arxiv_id}.pdf"
)
# Returns: "papers/1706.03762.pdf"
```

**Download Process**:
1. Create `papers/` directory if not exists
2. Download PDF from `paper.pdf_url`
3. Save as `{arxiv_id}.pdf`
4. Return local file path

**Result**: arXiv URL → Local PDF file path

---

## 3. PDF Text Extraction

### Module: `utils.py`

#### Step 3.1: Primary Extraction (pdfplumber)

```python
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
    except Exception as e:
        # Fallback to PyPDF2
        ...
```

**pdfplumber Advantages**:
- Better formatting preservation
- Handles tables better
- Maintains column structure
- Preserves line breaks

**Process**:
1. Open PDF file
2. Iterate through each page
3. Extract text from page
4. Add double newline between pages
5. Concatenate all pages

#### Step 3.2: Fallback Extraction (PyPDF2)

```python
except Exception as e:
    print(f"pdfplumber failed: {e}. Trying PyPDF2...")
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
```

**Fallback Trigger**:
- pdfplumber fails (corrupted PDF, unsupported format)
- Permission errors
- Encoding issues

**PyPDF2 Characteristics**:
- More robust (handles more PDF types)
- Less accurate formatting
- Faster processing
- Basic text extraction

#### Step 3.3: Text Structure

**Raw Extracted Text Example**:
```
Attention Is All You Need

Ashish Vaswani∗ Noam Shazeer∗ Niki Parmar∗ Jakob Uszkoreit∗

Abstract

The dominant sequence transduction models are based on complex recurrent or
convolutional neural networks...

1 Introduction

Recurrent neural networks, long short-term memory [13] and gated recurrent [7]
neural networks in particular, have been firmly established...
```

**Characteristics**:
- Contains all text from PDF
- Preserves section headers
- Includes page breaks (double newlines)
- May have formatting artifacts (∗, ligatures)
- Includes references and citations

---

## 4. PDF Image Extraction

### Module: `pdf_image_extractor.py`

#### Step 4.1: Embedded Image Extraction

```python
def extract_images_from_pdf(pdf_path: str) -> list:
    doc = fitz.open(pdf_path)  # PyMuPDF
    image_list = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images()  # Get all images on page
        
        for img_index, img in enumerate(images):
            xref = img[0]  # Image reference
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]  # png, jpg, etc.
```

**PyMuPDF (fitz) Process**:
1. Open PDF document
2. Iterate through pages
3. Get list of images on each page
4. Extract image data (bytes)
5. Get image format (PNG, JPEG, etc.)

#### Step 4.2: Image Filtering

```python
# Save and filter images
img_pil = Image.open(io.BytesIO(image_bytes))
width, height = img_pil.size

# Only keep substantial images (likely figures, not logos/icons)
if width > 200 and height > 150:
    image_list.append({
        'path': image_path,
        'page': page_num + 1,
        'size': (width, height),
        'index': img_index
    })
```

**Filtering Criteria**:
- Minimum width: 200 pixels
- Minimum height: 150 pixels
- Purpose: Remove small icons, logos, bullets

**Image Metadata**:
```python
{
    'path': 'extracted_images/page5_img2.png',
    'page': 5,
    'size': (800, 600),
    'index': 2
}
```

#### Step 4.3: Figure Region Extraction (Alternative)

```python
def extract_figure_regions(pdf_path: str) -> list:
    doc = fitz.open(pdf_path)
    
    for page_num in range(min(len(doc), 20)):  # First 20 pages
        page = doc[page_num]
        
        # Render entire page as high-res image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
        img_data = pix.tobytes("png")
```

**Full Page Rendering**:
- Renders page as image (2x resolution)
- Captures everything: text, figures, diagrams
- Useful when embedded images aren't extractable
- Larger file sizes

**Use Cases**:
- Vector graphics (not embedded as images)
- Complex diagrams
- Charts rendered as text/vectors

---

## 5. Text Cleaning and Normalization

### Module: `utils.py`

#### Step 5.1: Whitespace Normalization

```python
def clean_text(text: str) -> str:
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
```

**Before**:
```
The    dominant   sequence
transduction    models
```

**After**:
```
The dominant sequence transduction models
```

#### Step 5.2: Hyphenation Fixing

```python
# Fix broken sentences (heuristic)
text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
```

**Before**:
```
The trans-
former architecture
```

**After**:
```
The transformer architecture
```

**Pattern**: `word-` + `whitespace` + `word` → `wordword`

#### Step 5.3: Line Break Normalization

```python
# Normalize line breaks
text = text.replace('\n\n\n', '\n\n')
return text.strip()
```

**Purpose**:
- Remove excessive blank lines
- Standardize paragraph breaks
- Trim leading/trailing whitespace

---

## 6. Section Identification

### Module: `utils.py`

#### Step 6.1: Section Pattern Matching

```python
section_patterns = {
    'abstract': r'(?i)(abstract|summary)',
    'introduction': r'(?i)(introduction|background)',
    'methods': r'(?i)(method|methodology|approach|materials and methods)',
    'experiments': r'(?i)(experiment|evaluation|implementation)',
    'results': r'(?i)(result|finding)',
    'discussion': r'(?i)(discussion|analysis)',
    'conclusion': r'(?i)(conclusion|future work)',
    'references': r'(?i)(reference|bibliography)'
}
```

**Pattern Characteristics**:
- Case-insensitive (`(?i)`)
- Multiple variations per section
- Common academic paper structure

#### Step 6.2: Section Extraction Algorithm

```python
def identify_sections(text: str) -> Dict[str, str]:
    lines = text.split('\n')
    current_section = 'introduction'
    current_content = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if line is a section header
        is_header = False
        for section_name, pattern in section_patterns.items():
            if re.match(pattern, line_stripped) and len(line_stripped) < 50:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = section_name
                current_content = []
                is_header = True
                break
        
        if not is_header:
            current_content.append(line_stripped)
```

**Algorithm Steps**:
1. Split text into lines
2. Initialize current section as "introduction"
3. For each line:
   - Check if it matches a section pattern
   - Check if line is short (< 50 chars) - likely a header
   - If header: save previous section, start new section
   - If not header: add to current section content
4. Save final section

**Header Detection Criteria**:
- Matches section pattern (regex)
- Short length (< 50 characters)
- Standalone line

#### Step 6.3: Section Output Structure

```python
sections = {
    'abstract': "The dominant sequence transduction models...",
    'introduction': "Recurrent neural networks, long short-term memory...",
    'methods': "The Transformer follows this overall architecture...",
    'experiments': "We trained models on the standard WMT 2014...",
    'results': "Table 2 shows that the Transformer achieves...",
    'discussion': "In this work, we presented the Transformer...",
    'conclusion': "We are excited about the future of attention-based...",
    'references': "[1] Bahdanau, D., Cho, K., and Bengio, Y..."
}
```

**Dictionary Structure**:
- Key: Section name (standardized)
- Value: Full text content of section

---

## 7. Figure and Table Extraction

### Module: `utils.py`

#### Step 7.1: Figure Caption Pattern Matching

```python
# Pattern for figures
fig_pattern = r'(Figure|Fig\.?)\s+(\d+)[:\.]?\s*([^\n]+)'
for match in re.finditer(fig_pattern, text, re.IGNORECASE):
    figures.append({
        'type': 'figure',
        'number': match.group(2),
        'caption': match.group(3).strip()
    })
```

**Pattern Breakdown**:
- `(Figure|Fig\.?)` - Matches "Figure" or "Fig" or "Fig."
- `\s+` - One or more spaces
- `(\d+)` - Figure number (digits)
- `[:\.]?` - Optional colon or period
- `\s*` - Optional spaces
- `([^\n]+)` - Caption text (everything until newline)

**Matching Examples**:
- `Figure 1: Model architecture` → number=1, caption="Model architecture"
- `Fig. 2. Training curves` → number=2, caption="Training curves"
- `Figure 3 - Results comparison` → number=3, caption="- Results comparison"

#### Step 7.2: Table Caption Pattern Matching

```python
# Pattern for tables
table_pattern = r'(Table)\s+(\d+)[:\.]?\s*([^\n]+)'
for match in re.finditer(table_pattern, text, re.IGNORECASE):
    figures.append({
        'type': 'table',
        'number': match.group(2),
        'caption': match.group(3).strip()
    })
```

**Similar Pattern for Tables**:
- `Table 1: Performance metrics` → type="table", number=1
- `Table 2. Dataset statistics` → type="table", number=2

#### Step 7.3: Figure/Table Output Structure

```python
figures = [
    {
        'type': 'figure',
        'number': '1',
        'caption': 'The Transformer model architecture'
    },
    {
        'type': 'figure',
        'number': '2',
        'caption': 'Attention visualizations'
    },
    {
        'type': 'table',
        'number': '1',
        'caption': 'Machine translation results on WMT 2014'
    }
]
```

---

## 8. Complete Flow Diagram

### Full Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: PDF Path or arXiv URL/ID                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │ Input Detection│
            │   (main.py)    │
            └────────┬───────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌────────────────┐      ┌────────────────┐
│  arXiv URL/ID  │      │   Local PDF    │
└────────┬───────┘      └────────┬───────┘
         │                       │
         ▼                       │
┌────────────────────────────┐  │
│ arXiv Processing           │  │
│ (arxiv_downloader.py)      │  │
│                            │  │
│ 1. Extract ID from URL     │  │
│ 2. Search arXiv API        │  │
│ 3. Get metadata            │  │
│ 4. Download PDF            │  │
│ 5. Save to papers/         │  │
└────────┬───────────────────┘  │
         │                      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ PDF File Available   │
         │ (papers/XXXX.pdf)    │
         └──────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐      ┌────────────────┐
│ Text Extract  │      │ Image Extract  │
│ (utils.py)    │      │ (pdf_image_    │
│               │      │  extractor.py) │
│ 1. pdfplumber │      │                │
│ 2. PyPDF2     │      │ 1. PyMuPDF     │
│    (fallback) │      │ 2. Filter size │
│ 3. Get all    │      │ 3. Save images │
│    text       │      │                │
└───────┬───────┘      └────────┬───────┘
        │                       │
        ▼                       │
┌───────────────┐              │
│ Text Cleaning │              │
│ (utils.py)    │              │
│               │              │
│ 1. Normalize  │              │
│    whitespace │              │
│ 2. Fix hyphen │              │
│ 3. Clean      │              │
│    breaks     │              │
└───────┬───────┘              │
        │                      │
        ▼                      │
┌───────────────────┐          │
│ Section           │          │
│ Identification    │          │
│ (utils.py)        │          │
│                   │          │
│ 1. Pattern match  │          │
│ 2. Extract:       │          │
│    - Abstract     │          │
│    - Introduction │          │
│    - Methods      │          │
│    - Results      │          │
│    - Conclusion   │          │
└───────┬───────────┘          │
        │                      │
        ▼                      │
┌───────────────────┐          │
│ Figure/Table      │          │
│ Extraction        │          │
│ (utils.py)        │          │
│                   │          │
│ 1. Find captions  │          │
│ 2. Extract:       │          │
│    - Figure N     │          │
│    - Table N      │          │
│    - Captions     │          │
└───────┬───────────┘          │
        │                      │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Structured Data      │
        │                      │
        │ • paper_text         │
        │ • sections{}         │
        │ • figures[]          │
        │ • images[]           │
        │ • metadata{}         │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Agent Processing     │
        │ (7 specialized       │
        │  agents)             │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ OUTPUT:              │
        │ • Slide blueprint    │
        │ • PowerPoint (PPTX)  │
        └──────────────────────┘
```

---

## 9. Error Handling

### Error Handling at Each Stage

#### Stage 1: Input Detection
```python
try:
    paper_input = sys.argv[1]
except IndexError:
    # No command line argument
    paper_input = input("Enter paper path...")
```

**Errors Handled**:
- Missing input → Prompt user
- Invalid format → Show examples

#### Stage 2: arXiv Download
```python
try:
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(search.results())
except Exception as e:
    console.print(f"[red]Error downloading paper: {e}[/red]")
    raise
```

**Errors Handled**:
- Invalid arXiv ID → Clear error message
- Network failure → Retry logic (in arxiv library)
- API timeout → Exception with details

#### Stage 3: PDF Text Extraction
```python
try:
    with pdfplumber.open(pdf_path) as pdf:
        text = extract_with_pdfplumber(pdf)
except Exception as e:
    print(f"pdfplumber failed: {e}. Trying PyPDF2...")
    text = extract_with_pypdf2(pdf_path)
```

**Errors Handled**:
- Corrupted PDF → Fallback to PyPDF2
- Encrypted PDF → Try both libraries
- Unsupported format → Clear error message

#### Stage 4: PDF Image Extraction
```python
try:
    images = extract_images_from_pdf(pdf_path)
except Exception as e:
    console.print(f"[yellow]Could not extract images: {e}[/yellow]")
    images = []  # Continue without images
```

**Errors Handled**:
- No images in PDF → Empty list, continue
- Image corruption → Skip corrupted, process valid
- Permission errors → Warning, continue without images

#### Stage 5: Section Identification
```python
sections = identify_sections(text)
if not sections:
    # Fallback: treat entire text as one section
    sections = {'content': text}
```

**Errors Handled**:
- No sections found → Use entire text
- Malformed headers → Best-effort matching
- Missing sections → Continue with available sections

### Error Recovery Strategy

| Stage | Error Type | Recovery Action | User Impact |
|-------|-----------|-----------------|-------------|
| Input | Invalid path | Prompt for correct path | Must provide valid input |
| arXiv | Network failure | Retry 3 times | Slight delay |
| arXiv | Invalid ID | Show error, exit | Must provide valid ID |
| PDF Text | pdfplumber fails | Use PyPDF2 | Possible formatting loss |
| PDF Text | Both fail | Exit with error | Cannot proceed |
| PDF Images | Extraction fails | Continue without images | Text-only slides |
| Sections | No sections found | Use full text | Less structured output |
| Figures | No captions found | Empty list | No figure references |

---

## 10. Data Structures

### Internal Data Structures

#### Paper Text
```python
paper_text: str = """
Attention Is All You Need

Abstract
The dominant sequence transduction models...

1 Introduction
Recurrent neural networks...
"""
```

#### Sections Dictionary
```python
sections: Dict[str, str] = {
    'abstract': "The dominant sequence transduction models...",
    'introduction': "Recurrent neural networks...",
    'methods': "The Transformer follows...",
    'results': "Table 2 shows...",
    'conclusion': "We presented the Transformer..."
}
```

#### Figures List
```python
figures: List[Dict] = [
    {
        'type': 'figure',
        'number': '1',
        'caption': 'The Transformer model architecture'
    },
    {
        'type': 'table',
        'number': '1',
        'caption': 'Machine translation results'
    }
]
```

#### Images List
```python
images: List[Dict] = [
    {
        'path': 'extracted_images/page5_img2.png',
        'page': 5,
        'size': (800, 600),
        'index': 2
    }
]
```

#### Metadata Dictionary (arXiv only)
```python
metadata: Dict = {
    'title': 'Attention Is All You Need',
    'authors': ['Ashish Vaswani', 'Noam Shazeer', ...],
    'abstract': 'The dominant sequence transduction...',
    'published': '2017-06-12',
    'pdf_url': 'https://arxiv.org/pdf/1706.03762.pdf',
    'categories': ['cs.CL', 'cs.LG']
}
```

---

## 11. Performance Characteristics

### Processing Times

| Stage | Time (typical) | Bottleneck |
|-------|---------------|------------|
| arXiv Download | 5-15 seconds | Network speed |
| PDF Text Extraction | 1-5 seconds | PDF size, complexity |
| PDF Image Extraction | 2-10 seconds | Number of images |
| Text Cleaning | < 1 second | Text length |
| Section Identification | < 1 second | Text length |
| Figure Extraction | < 1 second | Text length |
| **Total Parsing** | **10-30 seconds** | **Network + PDF size** |

### Memory Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| PDF File | 1-10 MB | Stored on disk |
| Extracted Text | 0.1-1 MB | In memory |
| Extracted Images | 5-50 MB | Stored on disk |
| Sections Dict | 0.1-1 MB | In memory |
| **Total** | **~10-60 MB** | **Mostly disk** |

---

## 12. Libraries Used

### PDF Processing Libraries

#### pdfplumber
- **Purpose**: Primary text extraction
- **Advantages**: Better formatting, table handling
- **Disadvantages**: Can fail on some PDFs
- **Installation**: `pip install pdfplumber`

#### PyPDF2
- **Purpose**: Fallback text extraction
- **Advantages**: More robust, handles more formats
- **Disadvantages**: Less accurate formatting
- **Installation**: `pip install PyPDF2`

#### PyMuPDF (fitz)
- **Purpose**: Image extraction, page rendering
- **Advantages**: Fast, comprehensive image extraction
- **Disadvantages**: Larger dependency
- **Installation**: `pip install PyMuPDF`

### arXiv Library

#### arxiv
- **Purpose**: arXiv API interaction
- **Features**: Search, metadata, download
- **Installation**: `pip install arxiv`

### Image Processing

#### Pillow (PIL)
- **Purpose**: Image manipulation, size checking
- **Features**: Open, resize, filter images
- **Installation**: `pip install Pillow`

---

## Summary

### Complete Parsing Flow

1. **Input** → Detect type (arXiv URL/ID or local PDF)
2. **arXiv** → Download PDF if needed, extract metadata
3. **PDF Text** → Extract with pdfplumber (fallback: PyPDF2)
4. **PDF Images** → Extract with PyMuPDF, filter by size
5. **Clean** → Normalize whitespace, fix hyphenation
6. **Sections** → Pattern match headers, extract content
7. **Figures** → Extract captions with regex
8. **Output** → Structured data ready for agents

### Key Features

✅ **Robust**: Multiple fallback mechanisms
✅ **Comprehensive**: Text + images + metadata
✅ **Structured**: Organized sections and figures
✅ **Error-Tolerant**: Continues on partial failures
✅ **Fast**: 10-30 seconds total parsing time

### Data Flow

```
arXiv URL/PDF → Raw PDF → Text + Images → Cleaned Text → 
Sections + Figures → Structured Data → Agent Processing
```

**The parsing system transforms unstructured PDFs into structured, agent-ready data with comprehensive error handling and multiple extraction strategies.** 🚀
