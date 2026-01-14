"""Post-processing filter to detect and remove hallucinated facts."""
import re
from difflib import SequenceMatcher

def extract_factual_claims(bullet):
    """Extract factual claims from a bullet point."""
    claims = []
    
    # Extract numbers with context
    number_patterns = [
        (r'(\d+\.?\d*%)', 'percentage'),
        (r'(\d+\.?\d*[KMB])\s*(parameters|images|samples)', 'count'),
        (r'accuracy[:\s]+(\d+\.?\d*)', 'accuracy'),
        (r'learning rate[:\s]+(\d+\.?\d*)', 'learning_rate'),
        (r'batch size[:\s]+(\d+)', 'batch_size'),
        (r'(\d+)\s*(layers|epochs|classes)', 'architecture'),
    ]
    
    for pattern, claim_type in number_patterns:
        matches = re.finditer(pattern, bullet, re.IGNORECASE)
        for match in matches:
            claims.append({
                'type': claim_type,
                'value': match.group(1) if match.lastindex >= 1 else match.group(0),
                'text': match.group(0)
            })
    
    # Extract model/dataset names
    if re.search(r'\b[A-Z][a-zA-Z]*Net\b', bullet):  # ResNet, EfficientNet, etc.
        model_match = re.search(r'\b([A-Z][a-zA-Z]*Net[-\d]*)\b', bullet)
        if model_match:
            claims.append({
                'type': 'model_name',
                'value': model_match.group(1),
                'text': model_match.group(0)
            })
    
    return claims

def verify_claim_in_source(claim_text, source_text):
    """Check if a claim appears in the source text."""
    # Normalize texts
    claim_lower = claim_text.lower()
    source_lower = source_text.lower()
    
    # Direct substring match
    if claim_lower in source_lower:
        return True, 1.0
    
    # Check for numbers specifically
    claim_numbers = re.findall(r'\d+\.?\d*', claim_text)
    if claim_numbers:
        for num in claim_numbers:
            # Check if this exact number appears in source
            if num in source_text:
                return True, 0.8
    
    # Fuzzy match for similar phrases
    words = claim_lower.split()
    if len(words) >= 3:
        # Check if most words appear near each other in source
        word_positions = []
        for word in words:
            if len(word) > 3 and word in source_lower:
                word_positions.append(source_lower.find(word))
        
        if len(word_positions) >= len(words) * 0.7:
            # Most words found
            return True, 0.6
    
    return False, 0.0

def detect_hallucinations(slides, source_text):
    """Detect hallucinated content by comparing against source."""
    hallucinated_bullets = []
    verified_bullets = []
    
    for slide_idx, slide in enumerate(slides):
        for bullet_idx, bullet in enumerate(slide['bullets']):
            # Extract claims from bullet
            claims = extract_factual_claims(bullet)
            
            if not claims:
                # No specific claims to verify - keep it
                verified_bullets.append((slide_idx, bullet_idx, bullet, 'no_claims'))
                continue
            
            # Verify each claim
            all_verified = True
            min_confidence = 1.0
            
            for claim in claims:
                verified, confidence = verify_claim_in_source(claim['text'], source_text)
                if not verified:
                    all_verified = False
                    break
                min_confidence = min(min_confidence, confidence)
            
            if all_verified and min_confidence >= 0.6:
                verified_bullets.append((slide_idx, bullet_idx, bullet, f'verified_{min_confidence:.1f}'))
            else:
                hallucinated_bullets.append((slide_idx, bullet_idx, bullet, claims))
    
    return hallucinated_bullets, verified_bullets

def filter_hallucinated_bullets(slides, source_text=None):
    """Remove bullets that contain hallucinated facts."""
    if source_text is None:
        # Try to load from blueprint
        try:
            with open('output/slide_blueprint.txt', 'r', encoding='utf-8') as f:
                source_text = f.read()
        except:
            print("⚠️  Warning: Could not load source text for verification")
            return slides
    
    print("🔍 Verifying facts against source paper...")
    
    hallucinated, verified = detect_hallucinations(slides, source_text)
    
    if hallucinated:
        print(f"\n⚠️  Found {len(hallucinated)} potentially hallucinated bullets:")
        for slide_idx, bullet_idx, bullet, claims in hallucinated:
            print(f"  Slide {slide_idx+1}: {bullet[:70]}...")
            print(f"    Unverified claims: {[c['text'] for c in claims]}")
    
    # Create filtered slides
    filtered_slides = []
    for slide_idx, slide in enumerate(slides):
        filtered_bullets = []
        
        for bullet_idx, bullet in enumerate(slide['bullets']):
            # Check if this bullet is hallucinated
            is_hallucinated = any(
                s_idx == slide_idx and b_idx == bullet_idx 
                for s_idx, b_idx, _, _ in hallucinated
            )
            
            if not is_hallucinated:
                filtered_bullets.append(bullet)
        
        if filtered_bullets:
            filtered_slides.append({
                'title': slide['title'],
                'bullets': filtered_bullets
            })
    
    removed = len(slides) - len(filtered_slides) + sum(
        len(s['bullets']) for s in slides
    ) - sum(
        len(s['bullets']) for s in filtered_slides
    )
    
    if removed > 0:
        print(f"✓ Removed {removed} hallucinated bullets")
    else:
        print(f"✓ All bullets verified against source")
    
    return filtered_slides

def verify_numbers_consistency(slides):
    """Check for inconsistent numbers that might indicate hallucination."""
    warnings = []
    
    # Extract all numbers mentioned
    numbers_by_context = {}
    
    for slide in slides:
        for bullet in slide['bullets']:
            # Find accuracy mentions
            acc_match = re.search(r'accuracy[:\s]+(\d+\.?\d*)%?', bullet, re.IGNORECASE)
            if acc_match:
                acc = float(acc_match.group(1))
                if 'accuracy' not in numbers_by_context:
                    numbers_by_context['accuracy'] = []
                numbers_by_context['accuracy'].append((acc, bullet))
            
            # Find parameter counts
            param_match = re.search(r'(\d+\.?\d*)[KMB]?\s*parameters', bullet, re.IGNORECASE)
            if param_match:
                param = param_match.group(1)
                if 'parameters' not in numbers_by_context:
                    numbers_by_context['parameters'] = []
                numbers_by_context['parameters'].append((param, bullet))
    
    # Check for inconsistencies
    for context, values in numbers_by_context.items():
        if len(values) > 1:
            unique_values = set(v[0] for v in values)
            if len(unique_values) > 1:
                warnings.append(f"⚠️  Inconsistent {context} values: {unique_values}")
    
    if warnings:
        print("\n⚠️  Consistency warnings (may indicate hallucination):")
        for warning in warnings:
            print(f"  {warning}")
    
    return warnings

if __name__ == '__main__':
    # Test with example
    test_slides = [
        {
            'title': 'Results',
            'bullets': [
                'Achieves 85.2% accuracy on ImageNet',  # Would need to verify
                'Uses ResNet-50 architecture',  # Would need to verify
                'Trained with 100 epochs',  # Would need to verify
            ]
        }
    ]
    
    test_source = """
    Our model achieves 85.2% accuracy on the ImageNet dataset.
    We use the ResNet-50 architecture as our backbone.
    Training was performed for 100 epochs.
    """
    
    print("Testing hallucination detection:\n")
    hallucinated, verified = detect_hallucinations(test_slides, test_source)
    
    print(f"Verified: {len(verified)} bullets")
    print(f"Hallucinated: {len(hallucinated)} bullets")
