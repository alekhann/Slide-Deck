"""Agent definitions for the research paper to slide deck pipeline."""
from crewai import Agent, LLM
import config

# Initialize LLMs - Multi-Model Support
print(f"[AGENTS] Multi-Model Configuration:")
print(f"  Provider: {config.LLM_PROVIDER}")
print(f"  Primary Model (text): {config.PRIMARY_MODEL}")
print(f"  Secondary Model (PPTX): {config.SECONDARY_MODEL}")

if config.LLM_PROVIDER == 'ollama':
    # Primary LLM for text processing (summarization, structuring, verification)
    primary_llm = LLM(
        model=f"ollama_chat/{config.PRIMARY_MODEL}",
        api_base="http://localhost:11434",
        temperature=0.3
    )
    print(f"[AGENTS] Primary LLM: {config.PRIMARY_MODEL}")
    
    # Secondary LLM for PPTX generation (compilation, formatting)
    secondary_llm = LLM(
        model=f"ollama_chat/{config.SECONDARY_MODEL}",
        api_base="http://localhost:11434",
        temperature=0.5  # Slightly higher for creative formatting
    )
    print(f"[AGENTS] Secondary LLM: {config.SECONDARY_MODEL}")
else:
    # Groq fallback (uses same model for both)
    primary_llm = LLM(
        model=f"groq/{config.GROQ_MODEL}",
        api_key=config.GROQ_API_KEY,
        temperature=0.3
    )
    secondary_llm = primary_llm
    print(f"[AGENTS] Using Groq model: {config.GROQ_MODEL}")

# Legacy support
llm = primary_llm

# Paper Ingestion Agent (Primary Model)
ingestion_agent = Agent(
    role="Paper Ingestion Specialist",
    goal="Extract and clean text from research papers, preserving structure and context",
    backstory="Expert at parsing academic papers, extracting sections, figures, and maintaining document structure.",
    llm=primary_llm,
    verbose=True
)

# Section Summarization Agent (Primary Model - needs accuracy)
summarization_agent = Agent(
    role="Academic Summarizer",
    goal="Extract ONLY explicitly stated facts, numbers, and metrics from research papers - never infer or assume",
    backstory="""Expert fact extractor who ONLY reports what is explicitly written in the paper. 
    Never makes assumptions, never infers missing data, never rounds numbers. 
    If information isn't clearly stated, reports 'not specified' rather than guessing.
    Treats accuracy and precision as paramount - would rather omit information than risk being wrong.""",
    llm=primary_llm,
    verbose=True,
    max_iter=3  # Prevent infinite loops
)

# Slide Structuring Agent (Primary Model - needs accuracy)
structuring_agent = Agent(
    role="Slide Structure Architect",
    goal="Create slides using ONLY information from provided summaries - never add new data or make assumptions",
    backstory=f"""Meticulous slide designer who ONLY uses facts from the summaries provided. 
    Never invents numbers, never estimates metrics, never fills gaps with assumptions.
    If a summary doesn't contain specific data, leaves that bullet point out entirely.
    Believes in 'less is more' - better to have fewer accurate bullets than more questionable ones.
    Creates presentations with max {config.MAX_BULLETS_PER_SLIDE} bullets per slide and {config.MAX_WORDS_PER_BULLET} words per bullet.""",
    llm=primary_llm,
    verbose=True,
    max_iter=3  # Prevent infinite loops
)

# Visualization Recommendation Agent (Secondary Model - formatting task)
visualization_agent = Agent(
    role="Visual Content Advisor",
    goal="Identify and recommend figures, charts, and diagrams for slides",
    backstory="Specialist in selecting impactful visuals that enhance understanding of research findings.",
    llm=secondary_llm,
    verbose=True
)

# Compression Agent (Secondary Model - formatting task)
compression_agent = Agent(
    role="Content Compression Expert",
    goal="Convert prose into concise, slide-friendly bullets while preserving meaning",
    backstory=f"Master at condensing information into bullets of max {config.MAX_WORDS_PER_BULLET} words without losing core message.",
    llm=secondary_llm,
    verbose=True
)

# Verification Agent (Primary Model - needs accuracy)
verification_agent = Agent(
    role="Fact Verification Specialist",
    goal="Cross-check slide content against source text and flag unsupported claims",
    backstory="Meticulous fact-checker who ensures every bullet is grounded in the original paper.",
    llm=primary_llm,
    verbose=True
)

# Compilation Agent (Secondary Model - PPTX generation and formatting)
compilation_agent = Agent(
    role="Presentation Compiler",
    goal="Assemble final slide blueprint with presenter notes and verification report",
    backstory="Expert at creating cohesive, well-balanced presentations with comprehensive speaker support.",
    llm=secondary_llm,
    verbose=True
)
