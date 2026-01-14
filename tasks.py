"""Task definitions for the multi-agent pipeline."""
from crewai import Task
from agents import (
    ingestion_agent, summarization_agent, structuring_agent,
    visualization_agent, compression_agent, verification_agent,
    compilation_agent
)

def create_ingestion_task(paper_text):
    return Task(
        description=f"""Extract and organize the following research paper text:
        
        {paper_text[:1000]}...
        
        Parse the paper into sections (Abstract, Introduction, Methods, Results, Discussion, Conclusion).
        Extract figure captions and table references.
        Clean broken sentences and preserve page/section context.
        Output a structured dictionary with sections and their content.""",
        agent=ingestion_agent,
        expected_output="Structured dictionary with paper sections, figure captions, and cleaned text"
    )

def create_summarization_task(sections):
    # Limit content to avoid token limits
    sections_text = "\n\n".join([f"=== {name.upper()} ===\n{content[:800]}..." 
                                  for name, content in sections.items()])
    
    return Task(
        description=f"""Summarize each section of the research paper with SPECIFIC DETAILS.

        CRITICAL RULES TO PREVENT HALLUCINATIONS:
        1. ONLY extract information that is EXPLICITLY stated in the text
        2. If you don't see a specific number or metric, DO NOT make one up
        3. Use EXACT quotes and numbers from the paper
        4. If information is unclear, state "not specified" rather than guessing
        5. NEVER infer or assume data that isn't directly stated
        
        Paper sections:
        {sections_text}
        
        For EACH section, extract ONLY what is explicitly stated:
        - Exact numbers, percentages, and metrics (copy them exactly)
        - Specific model names, datasets, and techniques (use exact names from paper)
        - Concrete experimental results (only if numbers are given)
        - Actual findings with quantitative data (must be in the text)
        - Real methodology steps and parameters (as written in paper)
        
        Example of CORRECT extraction:
        "The paper states: EfficientNet-B0 achieves 85.2% top-1 accuracy on ImageNet with 5.3M parameters"
        
        Example of INCORRECT extraction (NEVER DO THIS):
        "The model achieves good accuracy" (too vague)
        "Accuracy improved by approximately 10%" (if exact number not given)
        "The model has around 50M parameters" (if exact number not stated)
        
        If a metric is not explicitly stated, write: "Metric not specified in this section"
        
        Output format: Section name followed by ONLY factual sentences with exact numbers from the text.""",
        agent=summarization_agent,
        expected_output="Detailed summaries with ONLY explicitly stated numbers, metrics, and concrete details - no inferences or assumptions"
    )

def create_structuring_task(summaries):
    return Task(
        description=f"""You are an expert presentation designer. Create a detailed, informative slide deck from the research paper.

        CRITICAL CONTENT RULES:
        1. Write ACTUAL CONTENT, not instructions like "mention this" or "explain that"
        2. Each bullet point must be a COMPLETE, INFORMATIVE statement
        3. EXPLAIN the concepts, don't just reference them
        4. Use SPECIFIC numbers, metrics, and details from the summaries
        5. Make each bullet self-contained and meaningful
        
        GOOD bullet examples (actual content):
        - Transformer architecture uses self-attention mechanism to process sequences in parallel, achieving 28.4 BLEU score on WMT 2014 English-German translation
        - Model consists of 6 encoder and 6 decoder layers with 8 attention heads per layer, totaling 65M parameters
        - Training completed in 3.5 days on 8 P100 GPUs using Adam optimizer with learning rate 0.0001
        - Outperforms previous LSTM-based models by 2.0 BLEU points while being 10x faster to train
        
        BAD bullet examples (NEVER DO THIS):
        - Mention the transformer architecture (not actual content)
        - Explain the attention mechanism (instruction, not content)
        - Discuss the training process (vague reference)
        - High accuracy achieved (no specifics)
        - Better than previous models (no numbers)
        
        SLIDE STRUCTURE:
        Slide 1: [Paper Title] - Title slide with paper name
        Slide 2: Introduction - What problem does this solve? Why is it important?
        Slide 3: Background - What existing approaches were used? What are their limitations?
        Slide 4-5: Methodology - How does the proposed approach work? What are the key innovations?
        Slide 6: Experimental Setup - What datasets? What metrics? What baselines?
        Slide 7-8: Results - What were the quantitative results? How does it compare to baselines?
        Slide 9: Discussion - What are the implications? Limitations? Future work?
        Slide 10: Conclusion - What are the key takeaways?
        
        FORMATTING RULES:
        - 3-4 informative bullets per slide
        - Each bullet: 15-25 words of actual content
        - NO labels like "Bullet:" or "Visual Notes:"
        - NO instructions like "mention" or "explain"
        - Write DIRECT, INFORMATIVE statements
        - Include specific numbers and metrics
        
        Output format:
        Slide 1: [Exact Paper Title from summaries]
        - [Complete informative statement with details]
        - [Another complete statement with specific data]
        - [Third statement with metrics or findings]
        
        Remember: You're creating the ACTUAL PRESENTATION CONTENT, not a plan for what to include!""",
        agent=structuring_agent,
        expected_output="Complete slide deck with actual informative content - not instructions or references, but real explanatory bullet points with specific details"
    )

def create_visualization_task(paper_content, slide_structure):
    return Task(
        description="""Recommend visuals for each slide:
        
        For each slide, identify:
        - Relevant figures/tables from the paper (use exact figure numbers from the paper)
        - What to highlight (specific curves, data points, comparisons)
        - ONLY recommend figures that are actually in the paper - do not suggest generic diagrams
        
        CRITICAL: Only recommend figures that exist in the source paper. If no relevant figure exists, state "No figure needed" instead of suggesting generic diagrams.
        
        Format: Slide N: Figure X from paper - [1-2 sentence description of what it shows]""",
        agent=visualization_agent,
        expected_output="Visual recommendations for each slide with specific figure numbers from the paper"
    )

def create_compression_task(slide_content):
    return Task(
        description="""Compress all slide bullets to meet formatting rules:
        
        - Each bullet must be ≤ 15 words
        - Preserve factual accuracy
        - Keep core meaning intact
        - Remove redundancy
        
        Review all bullets and compress where needed.""",
        agent=compression_agent,
        expected_output="Compressed slide content with all bullets meeting word limits"
    )

def create_verification_task(slides, original_text):
    return Task(
        description="""Verify each bullet against the original paper:
        
        For each bullet:
        1. Find supporting text in the original paper
        2. Note section/page context
        3. If no direct support found, flag as "interpretation" or "unverifiable"
        
        Calculate:
        - Total bullets
        - Verified bullets
        - Flagged bullets
        - Hallucination rate
        
        Output a verification report.""",
        agent=verification_agent,
        expected_output="Verification report with evidence pointers and hallucination metrics"
    )

def create_compilation_task(slides, visuals, verification):
    return Task(
        description="""You are an expert presentation compiler. Create the final presentation with ACTUAL CONTENT.

        CRITICAL RULES:
        1. First slide MUST be titled with the EXACT PAPER TITLE (not "Introduction" or "Overview")
        2. Write COMPLETE, INFORMATIVE bullet points - not instructions
        3. Each bullet must EXPLAIN the concept with specific details
        4. NO phrases like "mention", "explain", "discuss", "describe"
        5. NO labels like "Bullet:" or "Visual Notes:"
        
        STRUCTURE:
        Slide 1: [Exact Paper Title]
        - Brief overview of what the paper proposes
        - Key innovation or contribution
        - Main result or achievement
        
        Slide 2-3: Introduction & Background
        - What problem is being solved?
        - Why is it important?
        - What are current limitations?
        
        Slide 4-6: Methodology
        - How does the proposed approach work?
        - What are the key technical innovations?
        - What makes it different from existing methods?
        
        Slide 7-8: Experimental Results
        - What datasets were used?
        - What were the quantitative results?
        - How does it compare to baselines?
        
        Slide 9: Discussion & Conclusion
        - What are the key takeaways?
        - What are the implications?
        - What are limitations or future work?
        
        GOOD EXAMPLE (Slide 1 - Title Slide):
        Slide 1: Attention Is All You Need
        - Introduces Transformer architecture using only self-attention mechanisms, eliminating recurrence and convolutions entirely
        - Achieves 28.4 BLEU on WMT 2014 English-German translation, establishing new state-of-the-art
        - Trains in 3.5 days on 8 GPUs, 10x faster than previous sequence-to-sequence models
        
        BAD EXAMPLE (NEVER DO THIS):
        Slide 1: Introduction
        - Mention the transformer architecture
        - Explain the attention mechanism
        - Discuss the results
        
        FORMATTING:
        - Clean bullet points starting with "-"
        - NO "Bullet:" or "Visual Notes:" labels
        - 3-4 informative bullets per slide
        - Each bullet: complete statement with specifics
        
        Return the complete presentation with actual content, not a plan!""",
        agent=compilation_agent,
        expected_output="Complete presentation with paper title as first slide, followed by informative content slides with actual explanatory bullet points - no instructions or labels"
    )
