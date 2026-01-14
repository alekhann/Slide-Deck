# System Architecture

## Overview

Multi-agent system for converting research papers into professional presentations with intelligent figure matching and content verification.

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT                                    │
│         Research Paper (PDF/TXT/arXiv URL)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION PHASE                               │
│  • Download from arXiv (if URL/ID provided)                      │
│  • Extract text from PDF using PyPDF2/pdfplumber                 │
│  • Clean and normalize text                                      │
│  • Identify sections (Abstract, Intro, Methods, Results, etc.)   │
│  • Extract figure/table references                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              PARALLEL: FIGURE EXTRACTION                         │
│  • Extract embedded images from PDF (PyMuPDF)                    │
│  • Detect figure regions by finding captions                     │
│  • Crop and save figure regions                                  │
│  • Filter by size (remove icons/logos)                           │
│  • Output: extracted_figures/ directory                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AGENT PROCESSING CREW                           │
│                  (Powered by Ollama/Groq)                        │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  1. ACADEMIC SUMMARIZER                                   │   │
│  │     • Extract SPECIFIC details from each section          │   │
│  │     • Preserve exact numbers, metrics, model names        │   │
│  │     • Avoid generic descriptions                          │   │
│  │     • Output: Detailed factual summaries                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  2. SLIDE STRUCTURE ARCHITECT                             │   │
│  │     • Create slide-by-slide structure                     │   │
│  │     • Include concrete data (not generic phrases)         │   │
│  │     • Apply formatting rules (max 6 bullets/slide)        │   │
│  │     • Organize: Title → Intro → Methods → Results         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  3. VISUAL CONTENT ADVISOR                                │   │
│  │     • Recommend figures for each slide                    │   │
│  │     • Identify relevant charts/tables                     │   │
│  │     • Suggest diagram placements                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  4. CONTENT COMPRESSION EXPERT                            │   │
│  │     • Trim bullets to ≤18 words                           │   │
│  │     • Preserve factual accuracy                           │   │
│  │     • Remove redundancy                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  5. FACT VERIFICATION SPECIALIST                          │   │
│  │     • Cross-check bullets against source text             │   │
│  │     • Flag unverifiable claims                            │   │
│  │     • Calculate hallucination rate                        │   │
│  │     • Generate evidence pointers                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  6. PRESENTATION COMPILER                                 │   │
│  │     • Assemble final blueprint                            │   │
│  │     • Generate presenter notes with Q&A                   │   │
│  │     • Create verification report                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              SMART IMAGE MATCHING                                │
│  • Parse slide content (titles + bullets)                        │
│  • Analyze extracted figures (OCR + heuristics)                  │
│  • Calculate relevance scores                                    │
│  • Match most relevant figure to each slide                      │
│  • Apply minimum relevance threshold                             │
│  • Never reuse images                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PPTX GENERATION                                │
│  • Create professional title slide                               │
│  • Generate content slides with:                                 │
│    - Properly sized titles (word wrap enabled)                   │
│    - Bullet points with actual data                              │
│    - Matched figures/charts (two-column layout)                  │
│  • Apply professional color scheme                               │
│  • Add accent bars and styling                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUTS                                   │
│                                                                   │
│  📊 [Paper_Title].pptx                                           │
│     • Professional PowerPoint presentation                       │
│     • Smart-matched figures and charts                           │
│     • Clean, readable formatting                                 │
│                                                                   │
│  📄 slide_blueprint.txt                                          │
│     • Complete slide structure                                   │
│     • All bullet points                                          │
│     • Verification report with metrics                           │
│                                                                   │
│  🖼️ extracted_figures/ (directory)                               │
│     • All figures, charts, tables from PDF                       │
│     • High-quality PNG images                                    │
│     • Organized by page number                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Configuration (`config.py`)
- LLM provider selection (Ollama/Groq)
- Model configuration
- Formatting rules (bullets per slide, words per bullet)
- Output paths

### 2. Agents (`agents.py`)
- 7 specialized agents with distinct roles
- Configurable LLM backend (Ollama for local, Groq for cloud)
- Max iteration limits to prevent infinite loops
- Collaborative processing via CrewAI

### 3. Tasks (`tasks.py`)
- Detailed task definitions for each agent
- Emphasis on extracting SPECIFIC content (not generic)
- Clear input/output specifications
- Sequential execution with context passing

### 4. PDF Processing
- **arxiv_downloader.py**: Download papers from arXiv
- **utils.py**: Extract text, identify sections
- **extract_figures.py**: Extract figures, charts, tables
  - Embedded image extraction
  - Figure region detection via captions
  - Size-based filtering

### 5. Image Matching (`smart_image_matcher.py`)
- OCR-based text extraction from images
- Keyword-based relevance scoring
- Heuristic analysis (aspect ratio, content type)
- Intelligent fallback for result slides
- One-to-one slide-image mapping

### 6. PPTX Generation (`pptx_generator.py`)
- Professional slide templates
- Dynamic title sizing with word wrap
- Two-column layout (text + image)
- Color-coded design system
- Accent bars and styling

### 7. Pipeline Orchestration (`pipeline.py`)
- End-to-end workflow management
- Progress tracking with Rich console
- Error handling and recovery
- Unique filename generation

## Technology Stack

### Core Framework
- **Agent Framework**: CrewAI 0.80+
- **LLM Providers**: 
  - Ollama (local, no rate limits)
  - Groq (cloud, fast but limited)

### PDF & Image Processing
- **PyMuPDF (fitz)**: PDF rendering and image extraction
- **PyPDF2**: Text extraction
- **pdfplumber**: Table detection
- **Pillow (PIL)**: Image manipulation
- **pytesseract**: OCR for image analysis

### Presentation Generation
- **python-pptx**: PowerPoint file creation
- Custom styling and layouts

### Utilities
- **Rich**: Terminal UI and progress bars
- **python-dotenv**: Environment configuration
- **requests**: arXiv downloads

## Design Principles

### 1. Modularity
- Each agent has single, clear responsibility
- Loose coupling between components
- Easy to extend or replace agents

### 2. Verification First
- Built-in fact-checking agent
- Hallucination rate calculation
- Evidence pointers for all claims

### 3. Intelligence Over Automation
- Smart image matching (not random distribution)
- Content-aware figure selection
- Relevance scoring with thresholds

### 4. Flexibility
- Configurable LLM providers
- Adjustable formatting rules
- Multiple input formats

### 5. Robustness
- Fallback mechanisms for PDF extraction
- Error handling at each stage
- Graceful degradation (slides without images if needed)

### 6. Transparency
- Detailed verification reports
- Quality metrics (hallucination rate, verified bullets)
- Evidence pointers to source text

## Data Flow

```
Paper (PDF/URL)
    ↓
Text Extraction → Sections + Content
    ↓
Figure Extraction → Images + Charts
    ↓
Agent Processing → Structured Content
    ↓
Image Matching → Slide-Figure Pairs
    ↓
PPTX Generation → Final Presentation
```

## Agent Interaction Pattern

```
Summarizer → Architect → Advisor
                ↓
         Compression ← Verification
                ↓
            Compiler
```

Each agent receives output from previous agent(s) as context, enabling collaborative refinement.

## Performance Characteristics

### With Ollama (llama3.2:3b)
- **Speed**: 30-60 seconds per agent task
- **Rate Limits**: None (local)
- **Quality**: Good for factual extraction
- **Total Time**: 5-10 minutes for complete pipeline

### With Groq (llama-3.1-8b-instant)
- **Speed**: 5-10 seconds per agent task
- **Rate Limits**: 6000 tokens/minute (free tier)
- **Quality**: Excellent
- **Total Time**: 1-2 minutes (if no rate limits hit)

## Quality Metrics

The system tracks:
- **Total Bullets**: Number of bullet points generated
- **Verified Bullets**: Bullets with source evidence
- **Flagged Bullets**: Unverifiable or interpreted claims
- **Hallucination Rate**: Percentage of unsupported content
- **Images Matched**: Number of slides with relevant figures

Target metrics:
- Hallucination Rate: < 10%
- Verified Bullets: > 90%
- Images Matched: > 50% of slides

## Extension Points

### Add New Agent
1. Define agent in `agents.py`
2. Create task in `tasks.py`
3. Add to crew in `pipeline.py`

### Custom Image Matching
1. Modify `smart_image_matcher.py`
2. Adjust relevance scoring algorithm
3. Change threshold values

### Different LLM Provider
1. Add provider config in `config.py`
2. Update LLM initialization in `agents.py`
3. Set environment variable in `.env`

## Security Considerations

- API keys stored in `.env` (not committed)
- Local LLM option (Ollama) for sensitive papers
- No data sent to external services when using Ollama
- PDF processing done locally

## Future Enhancements

- [ ] Support for more LLM providers (OpenAI, Anthropic)
- [ ] Advanced figure captioning with vision models
- [ ] Interactive slide editing interface
- [ ] Batch processing multiple papers
- [ ] Custom presentation templates
- [ ] Speaker notes generation with timing
- [ ] Export to other formats (Google Slides, Keynote)
