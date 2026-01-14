# Simple Configuration Guide

## Single Model Setup (Recommended)

The simplest way to configure the system is to use one model for everything.

### Configuration (.env)

```env
MODEL=mistral
```

That's it! The system will use Mistral for all tasks.

## Changing Models

### Use a Different Model

Edit `.env`:
```env
MODEL=qwen2.5:7b
```

### Available Models

```env
MODEL=mistral          # Fastest (1-3 min per paper)
MODEL=qwen2.5:3b       # Fast (2-5 min per paper)
MODEL=qwen2.5:7b       # Balanced (5-10 min per paper)
MODEL=qwen2.5:14b      # High quality (10-15 min per paper)
MODEL=qwen2.5:32b      # Best quality (20-40 min per paper)
```

## Advanced: Multi-Model Setup

If you want to use different models for different tasks:

```env
# Use high-quality model for text processing
PRIMARY_MODEL=qwen2.5:14b

# Use fast model for formatting
SECONDARY_MODEL=mistral
```

**When to use**:
- You have enough RAM for multiple models
- You want quality for analysis but speed for formatting
- You're optimizing for specific use cases

## Current Setup

Your `.env` is set to:
```env
MODEL=mistral
```

This means:
- ✅ Single model (simplest)
- ✅ Fastest possible (1-3 minutes)
- ✅ Works on 4GB+ RAM
- ✅ Good quality for most papers

## Quick Reference

| Setting | Speed | Quality | RAM | Best For |
|---------|-------|---------|-----|----------|
| `MODEL=mistral` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 4GB+ | Testing, speed |
| `MODEL=qwen2.5:7b` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8GB+ | Balanced |
| `MODEL=qwen2.5:14b` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 16GB+ | Quality |
| Multi-model | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 16GB+ | Optimized |

## Examples

### Fastest Setup (Your Current Setup)
```env
MODEL=mistral
LLM_TIMEOUT=300
```

### Balanced Setup
```env
MODEL=qwen2.5:7b
LLM_TIMEOUT=600
```

### Quality Setup
```env
MODEL=qwen2.5:14b
LLM_TIMEOUT=900
```

### Optimized Multi-Model
```env
PRIMARY_MODEL=qwen2.5:14b
SECONDARY_MODEL=mistral
LLM_TIMEOUT=900
```

## Testing

After changing the model:

```bash
# Test configuration
python -c "import config; print(f'Model: {config.MODEL}')"

# Test model
ollama run mistral "Hello"

# Run pipeline
python main.py
```

## Summary

**Simple Setup** (Recommended):
```env
MODEL=mistral
```
One line, one model, fastest possible!

**Advanced Setup** (Optional):
```env
PRIMARY_MODEL=qwen2.5:14b
SECONDARY_MODEL=mistral
```
Different models for different tasks.

**Your current setup is perfect for speed!** 🚀
