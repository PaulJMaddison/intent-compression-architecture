# Intent Compression Architecture (ICA)

Clarification‑First Ambiguity Management for Large‑Scale Language Models

Author: Paul Maddison  
Email: paul.maddison.delimeg@gmail.com  
LinkedIn: https://www.linkedin.com/in/paul-maddison-b83395175/

---

## Overview

Intent Compression Architecture (ICA) is a structural framework designed to reduce ambiguity before full answer generation in large language models.

The core thesis is:

Ambiguity increases interpretive entropy.  
Interpretive entropy increases answer breadth.  
Answer breadth increases token consumption and reduces precision.

ICA introduces a clarification-first layer that collapses interpretive entropy prior to generation.

---

## The Structural Problem

Human questions frequently contain:

- Missing constraints  
- Implicit assumptions  
- Contested definitions  
- Referential ambiguity  
- Causal ambiguity  
- Task-type ambiguity  

When multiple interpretations are plausible, models implicitly distribute probability across interpretations. This produces broader, hedged responses that:

- Use more tokens  
- Reduce specificity  
- Increase instability in agent workflows  

This is a structural issue, not a stylistic one.

---

## Reverse Funnel Hypothesis

As user scale increases, interpretive variance increases.

Under preference optimisation systems, broadly acceptable responses are often rewarded when ambiguity exists. This can cause answers to generalise rather than narrow.

The result:

- Increased answer length  
- Reduced precision  
- Higher compute per resolved task  

ICA reverses this by narrowing interpretation before generation.

---

## ICA Mechanism

1. User query Q enters the system.
2. Ambiguity detection estimates interpretive entropy.
3. If entropy exceeds a calibrated threshold, a minimal clarification question C is generated.
4. User confirms intent T.
5. Final response is generated conditioned on (Q, T).

Generation shifts from:

P(A | Q)

to:

P(A | Q, T)

This narrows the output distribution.

---

## Ambiguity Taxonomy

ICA distinguishes:

- Definition ambiguity  
- Constraint ambiguity  
- Referential ambiguity  
- Causal ambiguity  
- Task-type ambiguity  

Clarification triggers only when ambiguity materially changes the correct answer.

---

## Interpretive Entropy Model

Let Q induce a distribution over interpretations I.

H(I | Q) represents interpretive uncertainty.

Traditional generation integrates across interpretations.

ICA collapses entropy before answer generation by confirming intent.

---

## Token Cost Modelling

Illustrative example:

Hedged response: 280 tokens  
Clarification: 22 tokens  
Conditioned response: 140 tokens  

ICA total: 162 tokens  
Reduction: ~42%

Even modest reductions scale significantly at high query volumes.

---

## Agent Branching Reduction

In agent systems, ambiguity increases branching factor (b) and depth (d).

Search complexity approximates O(b^d).

Example:

4^4 = 256 paths  
2^4 = 16 paths  

Early clarification dramatically reduces compute expansion.

---

## Clarification Optimisation Objective

Optimal clarification maximises entropy reduction per token:

argmax [ H(I|Q) − H(I|Q,C) ] / TokenCost(C)

Clarification must be information-efficient.

---

## Scaling Feedback Loop

Each clarification-confirmation interaction produces structured data:

(Q, C, T)

As this dataset grows:

- Ambiguity detection improves  
- Intent modelling improves  
- Clarification frequency decreases  
- Precision remains high  

Efficiency compounds over time.

---

## Risks and Trade-offs

- Over-clarification friction  
- Increased latency  
- False premise reinforcement  
- Ambiguity misclassification  
- Adversarial manipulation  

Mitigation requires calibrated thresholds and premise-aware design.

---

## Repository Contents

- ICA_Engineering_Design_Proposal_v4.pdf  
- Embedded architecture diagrams  
- README_FULL_v4.md  

---

## Status

Engineering design proposal.  
Formal large-scale empirical validation pending.

