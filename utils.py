"""Utility functions for paper processing."""
import re
import PyPDF2
import pdfplumber
from typing import Dict, List
import config
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber for better formatting."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
    except Exception as e:
        print(f"pdfplumber failed: {e}. Trying PyPDF2...")
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
    return text

def clean_text(text: str) -> str:
    """Clean extracted text by fixing common issues."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Fix broken sentences (heuristic)
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
    # Normalize line breaks
    text = text.replace('\n\n\n', '\n\n')
    return text.strip()

def identify_sections(text: str) -> Dict[str, str]:
    """Identify and extract major sections from paper."""
    sections = {}
    
    # Common section headers in research papers
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
    
    # Split text into potential sections
    lines = text.split('\n')
    current_section = 'introduction'
    current_content = []
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
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
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def extract_figures_and_tables(text: str) -> List[Dict[str, str]]:
    """Extract figure and table references with captions."""
    figures = []
    
    # Pattern for figures
    fig_pattern = r'(Figure|Fig\.?)\s+(\d+)[:\.]?\s*([^\n]+)'
    for match in re.finditer(fig_pattern, text, re.IGNORECASE):
        figures.append({
            'type': 'figure',
            'number': match.group(2),
            'caption': match.group(3).strip()
        })
    
    # Pattern for tables
    table_pattern = r'(Table)\s+(\d+)[:\.]?\s*([^\n]+)'
    for match in re.finditer(table_pattern, text, re.IGNORECASE):
        figures.append({
            'type': 'table',
            'number': match.group(2),
            'caption': match.group(3).strip()
        })
    
    return figures

def count_words_in_bullet(bullet: str) -> int:
    """Count words in a bullet point."""
    return len(bullet.split())

def ensure_output_directory():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

def save_output(filename: str, content: str):
    """Save content to output file."""
    ensure_output_directory()
    filepath = os.path.join(config.OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {filepath}")
