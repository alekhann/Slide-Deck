# Research Paper to Slide Deck Generator

## Quick Start

### 1. Install Ollama Model
```bash
ollama pull mistral
```

### 2. Configure
Your `.env` is already set to:
```env
MODEL=mistral
```

### 3. Run
```bash
python main.py
```

## Configuration

### Change Model
Edit `.env`:
```env
MODEL=qwen2.5:7b    # Better quality
MODEL=qwen2.5:14b   # High quality
MODEL=qwen2.5:32b   # Best quality
```

### Multi-Model (Optional)
For different models on different tasks:
```env
PRIMARY_MODEL=qwen2.5:14b
SECONDARY_MODEL=mistral
```

## Features

✅ Paper title as first slide
✅ Actual informative content (not "mention this")
✅ Specific numbers and details
✅ Clean formatting (no labels)
✅ Relevant images only
✅ Logical slide structure

## Speed

| Model | Time |
|-------|------|
| mistral | 1-3 min |
| qwen2.5:7b | 5-10 min |
| qwen2.5:14b | 10-15 min |
| qwen2.5:32b | 20-40 min |

## Documentation

- `SETUP.md` - This file
- `SIMPLE_CONFIG.md` - Configuration guide
- `CONTENT_QUALITY_FIXES.md` - Content improvements
- `SESSION_COMPLETE.md` - All changes made

## Troubleshooting

**Model not found?**
```bash
ollama pull mistral
```

**Want better quality?**
```bash
ollama pull qwen2.5:7b
# Edit .env: MODEL=qwen2.5:7b
```

That's it! Simple and fast. 🚀
