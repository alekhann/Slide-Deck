Multi-Agent Research Paper → Slide Deck Generator
Short description

An agentic AI pipeline that ingests a research paper (PDF or text) and outputs a presentation-ready slide blueprint and presenter notes. The system is driven by specialized agents (ingestion, summarization, structuring, visualization recommendation, verification, and compilation) that cooperate to produce concise, accurate, and slide-formatted content while minimizing hallucinations.

Intended use (one-line)

Feed a research paper and receive a verified, teacher-ready slide deck blueprint plus presenter notes and visual suggestions.

Inputs

A research paper in PDF or plain text form.

Optional: target slide count or style preference (concise / detailed / teaching).

Primary outputs

Slide blueprint (ordered list of slides with title, 3–6 bullets each, visual placeholder suggestions).

Presenter notes (short speaking points and likely audience questions/answers per slide).

Verification report (which bullets are directly supported by paper text and which require caution).

Optional: instructions for exporting to PPTX/Google Slides and simple diagram descriptions.

Core agents (roles)

Paper Ingestion Agent

Extracts raw text, retains page/section context, cleans broken sentences, isolates figure captions.

Section Summarization Agent

Produces concise summaries for Abstract, Introduction, Methods, Experiments, Results, Discussion, Conclusion.

Slide Structuring Agent

Maps summaries into slide-by-slide structure with titles and slide-brevity rules (<= 6 bullets, <= 12–15 words per bullet).

Visualization Recommendation Agent

Detects figures/tables and recommends what to show on each slide (charts, diagrams, table highlights).

Compression Agent

Converts prose into slide-friendly bullets while preserving core meaning.

Verification Agent

Cross-checks every bullet against the original text and returns an evidence pointer or flags the bullet.

Compilation Agent

Aggregates outputs into the final blueprint and presenter notes; balances slide length and flow.

Pipeline (sequential summary)

Accept paper file.

Ingestion: parse, clean, split into sections and chunks.

Summarize each section into short, focused outputs.

Extract candidate contributions and key claims.

Construct slide plan: title slide, motivation, problem, contributions, methods, experiments, results, conclusion, Q&A.

Compress long sentences into concise bullets.

Recommend visuals and placement.

Verify bullets against source text and mark unverifiable items.

Compile final blueprint and presenter notes; produce a short verification report.

Slide formatting rules (constraints)

Max 6 bullets per slide.

Max 12–15 words per bullet.

Use title + 3–6 bullets + optional visual note per slide.

Use a dedicated slide for each major contribution and for each principal experiment/result when applicable.

Keep a reproducibility or methodology slide when experiments are core to claims.

Verification & quality checks

For each bullet, attempt to locate a supporting sentence or snippet; attach section/page context.

Flag bullets lacking direct evidence as “interpretation” and suggest rewrite or citation.

Compute simple metrics: hallucination rate = flagged bullets / total bullets; average words per bullet.

Presenter notes

For every slide include 3–5 concise speaking points that expand the bullets without repeating them verbatim.

Include 2–3 likely audience questions and brief suggested answers for each slide.

Visualization guidance

For each identified figure/table: provide a 1–2 sentence description, suggested caption text, and an explicit note of what part to highlight on the slide (e.g., “highlight curve A vs. B, annotate crossover at epoch 12”).

If no figure exists but a diagram would help, suggest a simple schematic description (e.g., “3-block pipeline: encoder → fusion → classifier; annotate feature flows”).

Failure modes & mitigations

Poorly formatted or scanned PDFs: fallback to asking for plain text or manual upload of sections.

Hallucinated bullets: verifier flags them and the system either rewrites using direct snippets or marks them for human review.

Overlong slides: compilation agent redistributes content across more slides or trims bullets with compression rules.

Evaluation (quick checks to run)

Run on two sample papers (one empirical, one theoretical).

Measure hallucination rate and mean words per bullet.

Human judge 10 random bullets for fidelity (1–5 scale).

Inspect slide flow and visual placements manually.

Quick prompts / instructions for agent LLM calls (conceptual)

When summarizing: “Summarize this section into 2–3 slide-ready sentences preserving claims and metrics.”

When compressing: “Convert these sentences into concise, factual bullets, each ≤ 15 words.”

When verifying: “For each bullet, find a supporting snippet from the provided section text; return snippet location or mark unverifiable.”

When recommending visuals: “From the captions and nearby text, recommend the most informative figure or a simple diagram to illustrate this point.”