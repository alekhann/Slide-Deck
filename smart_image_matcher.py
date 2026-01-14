"""Smart image matching based on slide content relevance."""
import os
import glob
from PIL import Image
import pytesseract
from difflib import SequenceMatcher

def analyze_image_content(image_path):
    """Analyze image to determine what it likely contains."""
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Heuristics for image type
        aspect_ratio = width / height
        
        # Try OCR for any text
        try:
            text = pytesseract.image_to_string(img).lower()
        except:
            text = ""
        
        # Determine likely content type
        keywords = []
        if aspect_ratio > 1.5:
            keywords.append('chart')
        if 'atari' in text or 'game' in text or 'score' in text:
            keywords.extend(['atari', 'game', 'experimental', 'results'])
        if 'attention' in text or 'network' in text:
            keywords.extend(['attention', 'network', 'architecture'])
        if any(word in text for word in ['table', 'algorithm', 'method']):
            keywords.extend(['method', 'algorithm'])
            
        return ' '.join(keywords) + ' ' + text
    except:
        return ""

def calculate_relevance(slide_title, slide_bullets, image_keywords):
    """Calculate relevance score between slide content and image."""
    # Combine slide content
    slide_content = f"{slide_title} {' '.join(slide_bullets)}".lower()
    
    # Key terms to match
    key_terms = ['atari', 'game', 'attention', 'network', 'dqn', 'darqn', 
                 'experimental', 'results', 'performance', 'architecture',
                 'breakout', 'pong', 'space invaders', 'algorithm']
    
    # Count matches
    score = 0
    for term in key_terms:
        if term in slide_content and term in image_keywords:
            score += 5
    
    # Bonus for specific game names
    if any(game in slide_content for game in ['breakout', 'pong', 'space invaders']):
        if any(game in image_keywords for game in ['atari', 'game', 'score']):
            score += 10
    
    return score

def match_images_to_slides(slides, image_folder='extracted_images'):
    """Match most relevant image to each slide."""
    image_files = sorted(glob.glob(f'{image_folder}/*.png'))
    
    print(f"Analyzing {len(image_files)} images for relevance...")
    
    # Analyze all images (cache it)
    image_texts = {}
    for img_path in image_files:
        print(f"  Analyzing: {os.path.basename(img_path)}")
        image_texts[img_path] = analyze_image_content(img_path)
    
    # Match each slide to best image
    slide_images = []
    used_images = set()
    
    for i, slide in enumerate(slides):
        title = slide.get('title', '')
        bullets = slide.get('bullets', [])
        
        print(f"\nSlide {i+1}: {title}")
        
        # Calculate relevance for each image
        best_image = None
        best_score = 0
        
        for img_path in image_files:
            if img_path in used_images:
                continue
                
            score = calculate_relevance(title, bullets, image_texts[img_path])
            
            if score > best_score:
                best_score = score
                best_image = img_path
        
        # Only use image if relevance is above threshold
        if best_score > 3:  # Minimum relevance threshold
            slide_images.append({'path': best_image})
            used_images.add(best_image)
            print(f"  ✓ Matched: {os.path.basename(best_image)} (score: {best_score:.2f})")
        else:
            # For slides about experiments/results, use any remaining image
            if any(word in title.lower() + ' '.join(bullets).lower() 
                   for word in ['experimental', 'results', 'performance', 'atari']):
                # Pick first unused image
                for img_path in image_files:
                    if img_path not in used_images:
                        slide_images.append({'path': img_path})
                        used_images.add(img_path)
                        print(f"  ✓ Using: {os.path.basename(img_path)} (fallback for results slide)")
                        break
                else:
                    slide_images.append(None)
                    print(f"  ✗ No images remaining")
            else:
                slide_images.append(None)
                print(f"  ✗ No relevant image found (best score: {best_score:.2f})")
    
    return slide_images

def parse_blueprint_to_slides(blueprint_text):
    """Parse blueprint text into slide objects."""
    slides = []
    
    import re
    
    # Try format 1: Slide N: Title (with or without **)
    slide_pattern = r'(?:\*\*)?Slide \d+:\s*([^\n\*]+?)(?:\*\*)?$'
    matches = list(re.finditer(slide_pattern, blueprint_text, re.MULTILINE))
    
    if matches:
        # Parse **Slide N: Title** format
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(blueprint_text)
            content = blueprint_text[start:end]
            
            # Extract bullets and clean up labels
            bullets = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    bullet = line[1:].strip()
                    # Remove **Bullet:** or **Visual Notes:** labels
                    bullet = re.sub(r'^\*\*Bullet:\*\*\s*', '', bullet)
                    bullet = re.sub(r'^\*\*Visual Notes:\*\*\s*', '', bullet)
                    bullet = re.sub(r'^Bullet:\s*', '', bullet, flags=re.IGNORECASE)
                    bullet = re.sub(r'^Visual Notes:\s*', '', bullet, flags=re.IGNORECASE)
                    # Skip lines that are just visual notes
                    if bullet and not bullet.lower().startswith('visual'):
                        bullets.append(bullet)
            
            if bullets:
                slides.append({'title': title, 'bullets': bullets})
    else:
        # Try format 2: === TITLE ===
        sections = re.split(r'===\s*([^=]+)\s*===', blueprint_text)
        
        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break
                
            title = sections[i].strip()
            content = sections[i + 1].strip()
            
            # Extract bullets and clean up labels
            bullets = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    bullet = line[1:].strip()
                    # Remove **Bullet:** or **Visual Notes:** labels
                    bullet = re.sub(r'^\*\*Bullet:\*\*\s*', '', bullet)
                    bullet = re.sub(r'^\*\*Visual Notes:\*\*\s*', '', bullet)
                    bullet = re.sub(r'^Bullet:\s*', '', bullet, flags=re.IGNORECASE)
                    bullet = re.sub(r'^Visual Notes:\s*', '', bullet, flags=re.IGNORECASE)
                    # Skip lines that are just visual notes
                    if bullet and not bullet.lower().startswith('visual'):
                        bullets.append(bullet)
            
            if bullets:
                # Shorten long titles
                if len(title) > 50:
                    words = title.split()
                    if len(words) > 5:
                        title = ' '.join(words[:5]) + '...'
                
                slides.append({'title': title, 'bullets': bullets})
    
    return slides

if __name__ == '__main__':
    # Read blueprint
    with open('output/slide_blueprint.txt', 'r', encoding='utf-8') as f:
        blueprint = f.read()
    
    # Parse slides
    slides = parse_blueprint_to_slides(blueprint)
    print(f"Found {len(slides)} slides\n")
    
    # Match images
    matched_images = match_images_to_slides(slides)
    
    # Generate PPTX with matched images
    from pptx_generator import PPTXGenerator
    
    generator = PPTXGenerator()
    generator.add_title_slide(
        'Deep Attention Recurrent Q-Network',
        'AI-Generated Presentation',
        'Created by Multi-Agent System'
    )
    
    for i, slide in enumerate(slides):
        image_path = matched_images[i]['path'] if matched_images[i] else None
        generator.add_content_slide_with_image(
            slide['title'],
            slide['bullets'],
            image_path
        )
    
    output_path = 'output/Deep_Attention_Recurrent_Q_Network_smart_images.pptx'
    generator.save(output_path)
    
    print(f"\n✓ Generated: {output_path}")
    print(f"  - {len(slides)} content slides")
    print(f"  - {sum(1 for img in matched_images if img)} slides with relevant images")
