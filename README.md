# Intent Compression Architecture (ICA)

**Engineering design proposal** for a clarification-first layer that improves precision, reduces token waste, and stabilizes agent workflows.

## Plain-English summary
People often ask questions in shorthand. When a question is ambiguous (missing constraints, or using contested labels), models may hedge across multiple interpretations. That makes answers longer and less specific — and it costs more compute.

**ICA changes the flow:** when the system detects meaningful ambiguity, it asks one short, targeted clarifying question first. Once you confirm what you mean, it answers directly conditioned on that confirmed intent.

## Why it matters (in practice)
- **More precise answers:** better match to what the user actually meant.
- **Lower token usage:** fewer long, hedged answers written “just in case”.
- **More reliable agents:** coding/research agents do fewer loops and retries because constraints are confirmed early.
- **Clearer accountability:** responses can explicitly say “based on your definition…”, reducing misunderstandings.

## Contents
- **ICA_Engineering_Design_Proposal.pdf** — the main document (hybrid: plain English + architecture + evaluation plan)
- **diagrams/architecture.png** — pipeline diagram

## Core proposal (technical)
Add an explicit **Ambiguity Detection → Clarification → Intent Tag → Conditioned Answer** layer:
- If ambiguity is low → answer immediately
- If ambiguity is high → ask a minimal clarification question → answer conditioned on confirmed intent

## Evaluation plan (high-level)
Metrics proposed include:
- Total Tokens per Resolved Task (TTRT)
- Agent Loop Depth Reduction (ALDR)
- Response Specificity Index (RSI)
- Success Rate @ Budget

## Contact
Add your preferred contact method here (email / LinkedIn / X).
