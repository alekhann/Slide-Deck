# Research Paper to Slide Deck Generator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.80+-green.svg)](https://github.com/joaomdmoura/crewAI)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-orange.svg)](https://ollama.ai)

AI-powered multi-agent system that converts research papers into professional PowerPoint presentations with intelligent figure matching and content verification.

## 🎯 Overview

This system uses **CrewAI** to orchestrate 7 specialized AI agents that collaborate to:
- Extract and summarize research papers
- Generate informative slide content
- Match relevant figures to slides
- Verify facts against source material
- Create professional PowerPoint presentations

**Key Features**:
- ✅ Paper title as first slide
- ✅ Actual informative content (not "mention this")
- ✅ Specific numbers and details from paper
- ✅ Clean formatting without labels
- ✅ Intelligent figure matching
- ✅ Fact verification to prevent hallucinations
- ✅ Logical slide structure

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Failure Handling](#failure-handling)
- [Multi-User Scenarios](#multi-user-scenarios)
- [Why CrewAI?](#why-crewai)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

```bash
# 1. Install Ollama and model
ollama pull mistral

# 2. Clone and setup
git clone <repository-url>
cd research-paper-to-slides
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 3. Run
python main.py
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- [Ollama](https://ollama.ai) installed
- 4GB+ RAM (for Mistral model)

### Step-by-Step

1. **Install Ollama**
   ```bash
   # Download from https://ollama.ai
   # Then pull a model:
   ollama pull mistral
   ```

2. **Setup Python Environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   source env/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure**
   ```bash
   # .env is already configured with:
   MODEL=mistral
   ```

## 💻 Usage

### Basic Usage

```bash
python main.py
```

The system will prompt you for:
- Paper path (PDF file or arXiv URL)
- Target number of slides (optional)
- Presentation style (optional)

### With Arguments

```bash
# Local PDF
python main.py papers/your_paper.pdf

# arXiv URL
python main.py https://arxiv.org/abs/1706.03762

# arXiv ID
python main.py 1706.03762
```

### Output

Generated files in `output/` folder:
- `[Paper_Title].pptx` - PowerPoint presentation
- `slide_blueprint.txt` - Text version with all content

## 🏗️ Architecture

### System Flow

```
Paper (PDF/URL)
    ↓
Text Extraction → Sections + Content
    ↓
Figure Extraction → Images + Charts
    ↓
Agent Processing (7 Agents) → Structured Content
    ↓
Image Matching → Slide-Figure Pairs
    ↓
PPTX Generation → Final Presentation
```

### Multi-Agent System

The system uses **7 specialized agents**:

1. **Paper Ingestion Agent**
   - Extracts text from PDF
   - Identifies sections
   - Preserves structure

2. **Academic Summarizer**
   - Extracts specific facts
   - Preserves exact numbers
   - Avoids generic descriptions

3. **Slide Structure Architect**
   - Creates slide-by-slide structure
   - Applies formatting rules
   - Organizes logical flow

4. **Visual Content Advisor**
   - Recommends figures for slides
   - Identifies relevant charts
   - Suggests placements

5. **Content Compression Expert**
   - Trims bullets to optimal length
   - Preserves accuracy
   - Removes redundancy

6. **Fact Verification Specialist**
   - Cross-checks against source
   - Flags unverifiable claims
   - Calculates hallucination rate

7. **Presentation Compiler**
   - Assembles final blueprint
   - Generates presenter notes
   - Creates verification report

### Technology Stack

- **Agent Framework**: CrewAI 0.80+
- **LLM**: Ollama (local) or Groq (cloud)
- **PDF Processing**: PyMuPDF, PyPDF2, pdfplumber
- **Image Processing**: Pillow, pytesseract
- **Presentation**: python-pptx
- **UI**: Rich (terminal interface)

## 🛡️ Failure Handling

The system handles failures gracefully at each stage:

### Input Phase
- **File not found** → Clear error message, exit gracefully
- **Corrupted PDF** → Try alternative extraction methods
- **Network failure** → Retry with exponential backoff
- **Invalid arXiv ID** → Prompt for correct input

### Figure Extraction
- **No images found** → Continue with text-only slides
- **Image corruption** → Skip corrupted, process valid ones
- **Disk space full** → Use temporary directory
- **Permission denied** → Create temp directory

### Agent Processing
- **LLM timeout** → Retry with shorter prompt
- **Connection error** → Check if Ollama is running
- **Rate limit** → Wait and retry
- **Invalid response** → Generate minimal valid output
- **Hallucination** → Filter automatically

### Image Matching
- **No images available** → Create slides without images
- **OCR failure** → Use filename heuristics
- **Low relevance** → Skip image for that slide

### PPTX Generation
- **Disk full** → Save to temp directory
- **Permission denied** → Use alternative filename
- **Invalid data** → Create minimal slide
- **Missing image** → Continue without image

**See [FAILURE_HANDLING_AND_ARCHITECTURE.md](FAILURE_HANDLING_AND_ARCHITECTURE.md) for detailed failure scenarios.**

## 👥 Multi-User Scenarios

### Current Design
The system is designed for **single-user, sequential execution**.

### Concurrent Usage

**Scenario 1: Different Papers** ✅
```bash
# User 1
python main.py paper1.pdf  # Works

# User 2 (simultaneously)
python main.py paper2.pdf  # Works (different output files)
```

**Scenario 2: Same Paper** ⚠️
```bash
# User 1
python main.py paper.pdf

# User 2 (simultaneously)
python main.py paper.pdf  # Potential conflict
```

**Current Mitigation**: Automatic filename versioning
- `Paper.pptx`
- `Paper_Final_1.pptx`
- `Paper_Final_2.pptx`

### Making It Multi-User Safe

For production multi-user deployment, implement session-based isolation:

```python
# Each user gets unique session ID
session_id = str(uuid.uuid4())[:8]
output_dir = f"output/{session_id}/"
figures_dir = f"extracted_figures/{session_id}/"
```

**See [FAILURE_HANDLING_AND_ARCHITECTURE.md](FAILURE_HANDLING_AND_ARCHITECTURE.md) for multi-user architecture.**

## 🤔 Why CrewAI?

### Comparison with Alternatives

| Feature | CrewAI | LangGraph | LangChain |
|---------|--------|-----------|-----------|
| Agent Collaboration | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Role-Based Agents | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Sequential Tasks | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Learning Curve | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Development Speed | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

### Why CrewAI Was Chosen

1. **Native Multi-Agent Collaboration**
   - Agents collaborate automatically
   - No manual state management
   - Natural context passing

2. **Role-Based Design**
   - Agents have roles, goals, backstories
   - Perfect match for our use case
   - Each agent has specific expertise

3. **Sequential Processing**
   - Our pipeline is inherently sequential
   - `Process.sequential` matches perfectly
   - Simple and intuitive

4. **Development Speed**
   - Fastest to implement (2 days vs 4-5 days)
   - Less boilerplate code
   - Easy to maintain

5. **Code Clarity**
   ```python
   # CrewAI - Simple and clear
   crew = Crew(
       agents=[summarizer, architect, verifier],
       tasks=[summarize_task, structure_task, verify_task],
       process=Process.sequential
   )
   result = crew.kickoff()
   ```

### When to Use Each Framework

**Use CrewAI** (Our choice):
- Multi-agent collaboration
- Sequential workflows
- Role-based design
- Fast development

**Use LangGraph**:
- Complex branching workflows
- Conditional logic
- Cyclic workflows
- Fine-grained state control

**Use LangChain**:
- Simple chain-based workflows
- RAG applications
- Extensive tool ecosystem
- Prototyping

**See [FAILURE_HANDLING_AND_ARCHITECTURE.md](FAILURE_HANDLING_AND_ARCHITECTURE.md) for detailed comparison.**

## ⚙️ Configuration

### Change Model

Edit `.env`:
```env
MODEL=mistral          # Fastest (1-3 min)
MODEL=qwen2.5:7b       # Better quality (5-10 min)
MODEL=qwen2.5:14b      # High quality (10-15 min)
MODEL=qwen2.5:32b      # Best quality (20-40 min)
```

### Multi-Model Setup (Advanced)

Use different models for different tasks:
```env
PRIMARY_MODEL=qwen2.5:14b    # For text processing
SECONDARY_MODEL=mistral       # For formatting
```

### Formatting Rules

Edit `config.py`:
```python
MAX_BULLETS_PER_SLIDE = 5
MAX_WORDS_PER_BULLET = 25
```

## 📚 Documentation

### Quick References
- [START_HERE.txt](START_HERE.txt) - Quick start guide
- [SETUP.md](SETUP.md) - Detailed setup instructions
- [SIMPLE_CONFIG.md](SIMPLE_CONFIG.md) - Configuration guide

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [FAILURE_HANDLING_AND_ARCHITECTURE.md](FAILURE_HANDLING_AND_ARCHITECTURE.md) - Failure handling, multi-user, CrewAI rationale
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - File structure

### Improvements & Quality
- [CONTENT_QUALITY_FIXES.md](CONTENT_QUALITY_FIXES.md) - Content quality improvements
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Change log

### Troubleshooting
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

## 🔧 Troubleshooting

### Model Not Found
```bash
ollama pull mistral
```

### Ollama Not Running
```bash
# Check if running
ollama list

# Start Ollama
ollama serve
```

### Want Better Quality
```bash
ollama pull qwen2.5:7b
# Edit .env: MODEL=qwen2.5:7b
```

### Permission Errors
- Check write permissions on `output/` folder
- System will try temp directory as fallback

### No Images in Presentation
- Check if PDF has extractable images
- System continues without images if extraction fails

## 📊 Performance

| Model | Speed | Quality | RAM |
|-------|-------|---------|-----|
| mistral | 1-3 min | ⭐⭐⭐ | 4GB+ |
| qwen2.5:7b | 5-10 min | ⭐⭐⭐⭐ | 8GB+ |
| qwen2.5:14b | 10-15 min | ⭐⭐⭐⭐⭐ | 16GB+ |
| qwen2.5:32b | 20-40 min | ⭐⭐⭐⭐⭐ | 32GB+ |

## 🎓 Use Cases

- **Researchers**: Quickly create presentation from paper
- **Students**: Generate study slides from papers
- **Teachers**: Create lecture slides from research
- **Reviewers**: Summarize papers for presentations
- **Conferences**: Prepare talk slides efficiently

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional LLM providers
- Better figure captioning
- Interactive slide editing
- Batch processing
- Custom templates

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- **CrewAI** - Multi-agent framework
- **Ollama** - Local LLM inference
- **python-pptx** - PowerPoint generation
- **PyMuPDF** - PDF processing

## 📧 Contact

[Your Contact Information]

---

## 🚀 Quick Commands

```bash
# Setup
ollama pull mistral
python -m venv env
env\Scripts\activate
pip install -r requirements.txt

# Run
python main.py

# Change model
# Edit .env: MODEL=qwen2.5:7b

# Create submission package
python create_submission.py
```

---

**Made with ❤️ using CrewAI**
