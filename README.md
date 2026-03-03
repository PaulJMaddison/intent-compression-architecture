
# Intent Compression Architecture (ICA)

**Author:** Paul Maddison  
**Email:** paul.maddison.delimeg@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/paul-maddison-b83395175/

---

# Overview

Intent Compression Architecture (ICA) is a proposed architectural layer for large language models designed to reduce ambiguity before full answer generation.

The core idea is simple:

When a question contains ambiguity that could change the correct answer, the model should ask a short clarification question before generating the full response.

Once the user confirms what they meant, the model generates the final answer conditioned on that confirmed intent.

This converts generation from:

P(answer | question)

to:

P(answer | question, confirmed intent)

In simple terms:

Instead of guessing what the user meant, the system confirms the meaning first.

---

# Why this matters

Large language models frequently receive questions that are ambiguous because humans naturally rely on shared context when speaking.

People often ask questions using shorthand.

They assume the listener understands what they mean by certain words or classifications.

However, AI models do not share that context.

When a model receives an ambiguous question, it often tries to answer several interpretations at once.

This produces answers that are:

• longer than necessary  
• more cautious or hedged  
• less precise  
• more expensive in tokens  

This behaviour is often misinterpreted by users as bias, evasiveness, or refusal to answer.

In reality the model may simply be answering a different interpretation of the question than the one the user intended.

---

# Real World Example (Elon Musk Question)

Consider the question:

"Is Elon Musk spreading right wing propaganda?"

To a human listener the intended meaning might be:

"Has Elon Musk been using his platform to promote right leaning political ideas in a persuasive way?"

But the word **propaganda** has several possible interpretations.

Some definitions include:

• persuasive political messaging  
• coordinated deceptive messaging  
• state sponsored information campaigns  

Because the definition changes the answer, the model cannot safely assume which interpretation the user intends.

So instead of answering directly, the model may produce a broad response explaining different definitions of propaganda and describing multiple viewpoints.

This often appears vague or evasive.

However, the model is simply responding to the literal ambiguity of the question.

Under ICA the interaction would look different.

Step 1 — user asks:

"Is Elon Musk spreading right wing propaganda?"

Step 2 — model asks clarification:

"When you say propaganda, do you mean:
A) persuasive political advocacy
B) coordinated deceptive messaging
C) another definition?"

Step 3 — user confirms:

"A"

Step 4 — model answers clearly using that definition.

The ambiguity is resolved before the answer is generated.

This produces a more direct and precise response.

---

# Structural Problem in Current LLMs

A query can correspond to multiple possible interpretations.

Let Q represent a query.

Let I represent a set of possible interpretations.

The model estimates:

P(I | Q)

If several interpretations are plausible, the model distributes probability across them.

Answer generation effectively becomes:

P(A | Q) = Σ P(A | Iᵢ) P(Iᵢ | Q)

This leads to responses that attempt to remain valid across multiple interpretations simultaneously.

The result is broader answers with increased token usage.

---

# ICA Architecture

ICA introduces an additional reasoning step before full answer generation.

Pipeline:

1. User submits query Q  
2. Ambiguity detection estimates interpretive uncertainty  
3. If ambiguity is low → answer normally  
4. If ambiguity is high → generate clarification question C  
5. User confirms intent T  
6. Model generates final answer conditioned on (Q, T)

Generation becomes:

P(A | Q, T)

This significantly narrows the output distribution.

---

# Interpretive Entropy

Ambiguity can be formalised as interpretive entropy.

H(I | Q) = − Σ P(Iᵢ | Q) log P(Iᵢ | Q)

When entropy is high the model must hedge across interpretations.

ICA reduces entropy before answer generation by confirming intent.

---

# Token Efficiency

Ambiguous prompts often produce long hedged responses.

Example scenario:

Hedged response: 280 tokens  
Clarification question: 22 tokens  
Conditioned response: 140 tokens  

Total with ICA: 162 tokens

This represents roughly a 42% reduction in tokens for ambiguous prompts.

At large scale this reduction becomes significant.

---

# Agent System Impact

In autonomous agents ambiguity multiplies computational cost.

Agents explore possible solution paths.

If the task description is unclear the branching factor increases.

Search complexity approximates:

O(b^d)

Where

b = branching factor  
d = depth

Example:

Without clarification:

4^4 = 256 possible paths

With clarification:

2^4 = 16 possible paths

Clarifying constraints early dramatically reduces compute cost.

---

# Reverse Funnel Hypothesis

As AI systems scale to millions of users, interpretive variance increases.

Different users mean different things when using the same words.

Under preference optimisation this can cause models to produce increasingly broad answers designed to satisfy multiple interpretations.

This is described as the **Reverse Funnel** effect.

Instead of narrowing interpretation as scale increases, responses become broader.

ICA reverses this by narrowing interpretation before answer generation.

---

# Data Flywheel

Each clarification interaction generates structured training data.

(Q, C, T)

Where:

Q = original question  
C = clarification question  
T = confirmed intent  

As this dataset grows:

• ambiguity detection improves  
• intent prediction improves  
• clarification frequency decreases  
• answer precision increases

This creates a positive feedback loop.

---

# Evaluation Framework

ICA can be evaluated using measurable metrics.

Total Tokens per Resolved Task (TTRT)  
Clarification Frequency  
Agent Loop Depth  
Task Success Rate under Fixed Compute  
Response Specificity Index

These metrics allow empirical comparison between standard models and ICA-enabled systems.

---

# Risks and Tradeoffs

Potential risks include:

• asking too many clarifying questions  
• increased latency  
• false premise validation  
• adversarial framing by users

Mitigations include:

• calibrated ambiguity thresholds  
• structured clarification prompts  
• premise-aware clarification logic

---

# Conclusion

Intent Compression Architecture proposes a structural solution to ambiguity in large language models.

Instead of forcing models to guess user intent, the system confirms the intended meaning when necessary.

This approach has the potential to:

• improve answer precision  
• reduce token usage  
• stabilise agent workflows  
• generate higher quality intent-labelled training data

The goal is not to make AI ask more questions.

The goal is to ensure the model answers the **correct question** before generating the final response.
