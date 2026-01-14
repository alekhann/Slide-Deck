"""Organize slides in logical presentation order."""
import re

def classify_slide(title, bullets):
    """Classify slide type based on title and content."""
    title_lower = title.lower()
    content = ' '.join(bullets).lower()
    
    # Classification rules - following standard research presentation structure
    if any(word in title_lower for word in ['introduction', 'intro', 'overview', 'abstract']):
        return 'introduction', 1
    
    if any(word in title_lower for word in ['background', 'related work', 'motivation', 'problem', 'prior work']):
        return 'background', 2
    
    if any(word in title_lower for word in ['method', 'approach', 'architecture', 'model', 'design', 'proposed', 'algorithm']):
        return 'methodology', 3
    
    if any(word in title_lower for word in ['experiment', 'evaluation', 'setup', 'implementation', 'training']):
        return 'experimental', 4
    
    if any(word in title_lower for word in ['result', 'performance', 'comparison', 'analysis', 'findings']):
        return 'results', 5
    
    if any(word in title_lower for word in ['discussion', 'limitation', 'future work', 'implication']):
        return 'discussion', 6
    
    if any(word in title_lower for word in ['conclusion', 'summary', 'takeaway']):
        return 'conclusion', 7
    
    # Content-based classification if title is ambiguous
    if 'architecture' in content or 'model' in content or 'layer' in content or 'network' in content:
        return 'methodology', 3
    
    if 'accuracy' in content or 'performance' in content or 'outperform' in content or 'score' in content:
        return 'results', 5
    
    if 'training' in content or 'optimizer' in content or 'hyperparameter' in content or 'epoch' in content:
        return 'experimental', 4
    
    if 'limitation' in content or 'future' in content or 'improve' in content:
        return 'discussion', 6
    
    # Default to methodology if unclear
    return 'other', 3.5

def reorder_slides(slides):
    """Reorder slides in logical presentation flow: Introduction → Background → Methodology → Experimental Results → Discussion → Conclusion."""
    if not slides:
        return slides
    
    # Classify each slide
    classified = []
    for i, slide in enumerate(slides):
        slide_type, order = classify_slide(slide['title'], slide['bullets'])
        classified.append({
            'slide': slide,
            'type': slide_type,
            'order': order,
            'original_index': i
        })
    
    # Sort by order (Introduction → Background → Methodology → Experimental → Results → Discussion → Conclusion)
    classified.sort(key=lambda x: (x['order'], x['original_index']))
    
    # Extract reordered slides
    reordered = [item['slide'] for item in classified]
    
    # Print reordering info with proper structure
    print("\n📋 Slide organization (Standard Research Presentation Structure):")
    print("   Paper Title → Introduction → Background → Methodology → Experimental Results → Discussion → Conclusion")
    current_section = None
    for i, item in enumerate(classified):
        if item['type'] != current_section:
            current_section = item['type']
            print(f"\n  {current_section.upper()}:")
        print(f"    {i+1}. {item['slide']['title'][:60]}")
    
    return reordered

def merge_duplicate_sections(slides):
    """Merge slides with similar titles/sections."""
    if not slides:
        return slides
    
    merged = []
    skip_indices = set()
    
    for i, slide in enumerate(slides):
        if i in skip_indices:
            continue
        
        # Check if next slide is similar
        current_title = slide['title'].lower()
        current_bullets = slide['bullets'][:]
        
        for j in range(i + 1, len(slides)):
            if j in skip_indices:
                continue
            
            next_title = slides[j]['title'].lower()
            
            # Check for similar titles
            similarity = similar_titles(current_title, next_title)
            if similarity > 0.7:
                # Merge bullets
                for bullet in slides[j]['bullets']:
                    if bullet not in current_bullets:
                        current_bullets.append(bullet)
                skip_indices.add(j)
                print(f"  ℹ️  Merged duplicate: '{slides[j]['title']}' into '{slide['title']}'")
        
        # Add merged slide (limit bullets to 3-4, keep most important)
        merged.append({
            'title': slide['title'],
            'bullets': current_bullets[:4]
        })
    
    return merged

def similar_titles(title1, title2):
    """Calculate similarity between two titles."""
    words1 = set(title1.split())
    words2 = set(title2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def organize_presentation(slides):
    """Full organization: merge duplicates and reorder."""
    print("\n🔄 Organizing presentation...")
    
    # First merge duplicates
    slides = merge_duplicate_sections(slides)
    
    # Then reorder logically
    slides = reorder_slides(slides)
    
    print(f"\n✓ Final presentation: {len(slides)} slides")
    
    return slides

if __name__ == '__main__':
    # Test
    test_slides = [
        {'title': 'Model Architecture', 'bullets': ['Uses transformer']},
        {'title': 'Experimental Results', 'bullets': ['85% accuracy']},
        {'title': 'Introduction', 'bullets': ['Paper overview']},
        {'title': 'Background', 'bullets': ['Related work']},
        {'title': 'Training Setup', 'bullets': ['Adam optimizer']},
        {'title': 'Conclusion', 'bullets': ['Summary']},
    ]
    
    organized = organize_presentation(test_slides)
    
    print("\nFinal order:")
    for i, slide in enumerate(organized):
        print(f"{i+1}. {slide['title']}")
