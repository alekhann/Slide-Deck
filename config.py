"""Configuration settings for the multi-agent pipeline."""
import os
from dotenv import load_dotenv

load_dotenv()

# Model Configuration
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')  # Options: 'groq', 'ollama'

# Single model for all tasks (simplest setup)
MODEL = os.getenv('MODEL', 'mistral')

# Multi-model support (optional - for advanced users)
PRIMARY_MODEL = os.getenv('PRIMARY_MODEL', MODEL)  # Defaults to MODEL if not set
SECONDARY_MODEL = os.getenv('SECONDARY_MODEL', MODEL)  # Defaults to MODEL if not set

# Legacy support
OLLAMA_MODEL = MODEL

# Debug output
if PRIMARY_MODEL == SECONDARY_MODEL:
    print(f"[CONFIG] LLM_PROVIDER: {LLM_PROVIDER}")
    print(f"[CONFIG] MODEL: {MODEL} (single model for all tasks)")
else:
    print(f"[CONFIG] LLM_PROVIDER: {LLM_PROVIDER}")
    print(f"[CONFIG] PRIMARY_MODEL (text processing): {PRIMARY_MODEL}")
    print(f"[CONFIG] SECONDARY_MODEL (PPTX generation): {SECONDARY_MODEL}")

# Slide Formatting Rules
MAX_BULLETS_PER_SLIDE = 5  # Keep slides focused with 3-4 bullets
MAX_WORDS_PER_BULLET = 25  # Allow detailed, self-explanatory bullets
MIN_BULLETS_PER_SLIDE = 3  # Minimum 3 bullets for substance

# No timeout - let the model take as long as it needs

# Processing Settings
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
MAX_SECTION_LENGTH = 800  # Limit section text to avoid token overload

# Output Settings
OUTPUT_DIR = "output"
SLIDES_OUTPUT = "slide_blueprint.txt"
PRESENTER_NOTES_OUTPUT = "presenter_notes.txt"
VERIFICATION_REPORT_OUTPUT = "verification_report.txt"
