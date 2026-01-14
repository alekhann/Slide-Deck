"""Intelligent figure matching using agent recommendations and content analysis."""
import os
import re
import glob
from PIL import Image

def extract_figure_recommendations(blueprint_text):
    """Extract figure recommendations from Visual Content Advisor output."""
    recommendations = {}
    
    # Look for visual recommendations in blueprint
    # Format: "Slide N: ... Figure X: description"
    slide_pattern = r'Slide (\d+):[^\n]*'
    figure_pattern = r'Figure (\d+|[A-Z]):|Table (\d+):|diagram|chart|plot|graph'
    
    lines = blueprint_text.split('\n')
    current_slide = None
    
    for i, line in enumerate(lines):
        # Check if this is a slide header
        slide_match = re.search(slide_pattern, line)
        if slide_match:
            current_slide = int(slide_match.group(1))
            recommendations[current_slide] = []
        
        # Check for figure mentions
        if current_slide and re.search(figure_pattern, line, re.IGNORECASE):
            # Look at surrounding lines for context
            context = ' '.join(lines[max(0, i-2):min(len(lines), i+3)])
            recommendations[current_slide].append({
                'line': line.strip(),
                'context': context
            })
    
    return recommendations

def analyze_image_type(image_path):
    """Determine what type of figure this is (chart, diagram, table, etc)."""
    try:
        img = Image.open(image_path)
        width, height = img.size
        aspect_ratio = width / height
        
        # Heuristics based on image characteristics
        image_type = []
        
        # Wide images are often charts/plots
        if aspect_ratio > 1.5:
            image_type.append('chart')
        
        # Square-ish images might be diagrams
        if 0.8 < aspect_ratio < 1.2:
            image_type.append('diagram')
        
        # Tall images might be tables or architecture diagrams
        if aspect_ratio < 0.7:
            image_type.append('table')
        
        # Check filename for hints
        filename = os.path.basename(image_path).lower()
        if 'figure' in filename:
            # Extract figure number
            fig_match = re.search(r'figure[_\s]*(\d+)', filename)
            if fig_match:
                image_type.append(f'figure_{fig_match.group(1)}')
        
        return image_type if image_type else ['unknown']
    except:
        return ['unknown']

def match_slide_to_figure(slide_title, slide_bullets, slide_num, recommendations, available_images, paper_keywords=None):
    """Match a slide to the most relevant figure - ONLY if truly relevant."""
    slide_content = f"{slide_title} {' '.join(slide_bullets)}".lower()
    
    # Extract paper-specific keywords (model names, techniques)
    if paper_keywords is None:
        paper_keywords = []
    
    # Check if there's a specific recommendation for this slide
    if slide_num in recommendations:
        for rec in recommendations[slide_num]:
            # Look for figure numbers mentioned
            fig_match = re.search(r'figure\s*(\d+)', rec['line'], re.IGNORECASE)
            if fig_match:
                fig_num = fig_match.group(1)
                # Find image with this figure number
                for img_path in available_images:
                    if f'figure_{fig_num}' in os.path.basename(img_path).lower():
                        return img_path, 'recommended'
    
    # Content-based matching - be more strict
    keywords = {
        'architecture': ['architecture', 'model', 'network', 'structure', 'design', 'layer'] + paper_keywords,
        'results': ['results', 'performance', 'accuracy', 'comparison', 'evaluation', 'experiment', 'score'],
        'method': ['method', 'approach', 'algorithm', 'procedure', 'mechanism', 'process'],
        'training': ['training', 'optimization', 'learning', 'convergence', 'loss', 'epoch'],
        'data': ['data', 'dataset', 'samples', 'distribution', 'augmentation', 'preprocessing'],
    }
    
    # Score each image
    best_image = None
    best_score = 0
    
    for img_path in available_images:
        score = 0
        img_types = analyze_image_type(img_path)
        img_filename = os.path.basename(img_path).lower()
        
        # Match based on content keywords
        for category, words in keywords.items():
            if any(word in slide_content for word in words):
                # Prefer certain image types for certain content
                if category == 'architecture' and 'diagram' in img_types:
                    score += 10
                elif category == 'results' and 'chart' in img_types:
                    score += 10
                elif category == 'data' and 'table' in img_types:
                    score += 8
                else:
                    score += 3
        
        # Prefer images from relevant pages
        # Extract page number from filename
        page_match = re.search(r'page(\d+)', img_filename)
        if page_match:
            page_num = int(page_match.group(1))
            # Results usually in later pages
            if 'results' in slide_content and page_num > 4:
                score += 5
            # Methods usually in middle pages
            elif 'method' in slide_content and 2 < page_num < 6:
                score += 5
            # Architecture usually in early-middle pages
            elif 'architecture' in slide_content and 2 < page_num < 5:
                score += 5
        
        # Boost score if paper keywords match filename
        for keyword in paper_keywords:
            if keyword in img_filename:
                score += 8
        
        # Penalize embedded images (usually small icons/logos)
        if 'embedded' in img_filename:
            score -= 5
        
        if score > best_score:
            best_score = score
            best_image = img_path
    
    # Only return if score is meaningful - be stricter
    if best_score >= 8:  # Increased threshold from 5 to 8
        return best_image, f'matched_score_{best_score}'
    
    return None, 'no_match'

def smart_match_figures(slides, image_folder='extracted_figures', blueprint_text=''):
    """Intelligently match figures to slides."""
    # Get all available images
    image_files = sorted(glob.glob(f'{image_folder}/*.png'))
    
    if not image_files:
        print(f"⚠️  No images found in {image_folder}/")
        return [None] * len(slides)
    
    print(f"\n🎨 Smart figure matching ({len(image_files)} figures available)...")
    
    # Extract paper-specific keywords (model names, techniques)
    paper_keywords = []
    # Look for capitalized terms that might be model names
    model_pattern = r'\b([A-Z][a-z]*(?:[A-Z][a-z]*)+)\b'
    for match in re.finditer(model_pattern, blueprint_text):
        keyword = match.group(1)
        if len(keyword) > 4:  # Skip short acronyms
            paper_keywords.append(keyword.lower())
    
    # Extract recommendations from blueprint
    recommendations = extract_figure_recommendations(blueprint_text)
    
    # Match each slide
    matched_images = []
    used_images = set()
    
    for i, slide in enumerate(slides):
        slide_num = i + 1
        title = slide.get('title', '')
        bullets = slide.get('bullets', [])
        
        # Get available images (not yet used)
        available = [img for img in image_files if img not in used_images]
        
        if not available:
            matched_images.append(None)
            print(f"  Slide {slide_num}: No more figures available")
            continue
        
        # Match
        matched_img, reason = match_slide_to_figure(
            title, bullets, slide_num, recommendations, available, paper_keywords
        )
        
        if matched_img:
            matched_images.append({'path': matched_img})
            used_images.add(matched_img)
            print(f"  ✓ Slide {slide_num} ({title[:40]}...): {os.path.basename(matched_img)} ({reason})")
        else:
            matched_images.append(None)
            print(f"  ○ Slide {slide_num} ({title[:40]}...): No relevant figure")
    
    return matched_images

if __name__ == '__main__':
    # Test
    test_slides = [
        {'title': 'Model Architecture', 'bullets': ['Uses transformer architecture']},
        {'title': 'Experimental Results', 'bullets': ['Achieves 85% accuracy']},
        {'title': 'Training Procedure', 'bullets': ['Trained with Adam optimizer']},
    ]
    
    matched = smart_match_figures(test_slides, 'extracted_figures')
    print(f"\nMatched {sum(1 for m in matched if m)} out of {len(test_slides)} slides")
