# Troubleshooting: "Found 0 slides" Error

## Problem
Running `create_final_pptx.py` shows:
```
Found 0 slides
```

## Root Cause
The `output/slide_blueprint.txt` file only contains a verification report, not the actual slide content. The parser can't find slides because they're not in the file.

## Solution

### Option 1: Run the Full Pipeline (Recommended)

Generate fresh slides from a paper:

```bash
python main.py
```

When prompted:
- Enter paper path: `papers/1706.03762.pdf` (or any paper)
- Target slides: Press Enter (or specify a number)
- Style: Press Enter (uses default "concise")

This will:
1. Process the paper
2. Generate slide content
3. Create `output/slide_blueprint.txt` with actual slides
4. Create the PowerPoint presentation automatically

### Option 2: Check Existing Blueprint

If you recently ran the pipeline, check if the blueprint has the correct format:

```bash
# View the blueprint file
type output\slide_blueprint.txt
```

The blueprint should contain slides in this format:
```
Slide 1: Title Here
- Bullet point 1
- Bullet point 2
- Bullet point 3

Slide 2: Another Title
- Bullet point 1
- Bullet point 2
```

OR this format:
```
**Slide 1: Title Here**
- Bullet point 1
- Bullet point 2

**Slide 2: Another Title**
- Bullet point 1
- Bullet point 2
```

### Option 3: Use Existing Presentations

If you have existing `.pptx` files in the output folder, you can use those directly:
- `output/Attention_Is_All_You_Need.pptx`
- `output/SwinTransformer_Model_Final_2.pptx`
- etc.

## Why This Happened

The `slide_blueprint.txt` file currently only contains:
```
Verification Report Summary:
- Slide 1: Attention Is All You Need - Verified...
- Slide 2: EfficientNet-B0 - Verified...
```

This is just a verification report, not the actual slide content. The parser looks for:
- `Slide N: Title` patterns
- `=== TITLE ===` patterns

Neither exists in the current file.

## Next Steps

1. **Run the full pipeline** with `python main.py` to generate fresh slides
2. The pipeline will automatically create the PowerPoint file
3. Check `output/` folder for the generated `.pptx` file

## Testing the Fixes

After running `main.py`, the generated slides should have:
- ✅ No "**Bullet:**" or "**Visual Notes:**" labels
- ✅ Clean bullet points
- ✅ Only relevant images from the paper
- ✅ Proper slide order: Title → Intro → Background → Method → Results → Discussion → Conclusion

## Quick Test Command

```bash
# Run with a specific paper
python main.py papers/1706.03762.pdf

# Or run interactively
python main.py
```
