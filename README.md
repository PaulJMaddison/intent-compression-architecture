# Intent Compression Architecture (ICA)

**Clarification-first ambiguity management for large-scale language models**

**Author:** Paul Maddison  
**Email:** paul.maddison.delimeg@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/paul-maddison-b83395175/

---

## What this is

ICA is an engineering proposal to improve **precision**, **token efficiency**, and **agent reliability** by resolving **meaningful ambiguity before answering**.

Large language models often answer the literal wording of a question even when the user’s meaning depends on unstated definitions or missing constraints. When a query has multiple plausible interpretations, the model tends to hedge across them, producing broader answers that use more tokens and feel less precise.

ICA adds a clarification-first layer that asks **one minimal, targeted clarifying question** only when the ambiguity would materially change the answer. Once the user confirms intent, the model answers conditioned on that confirmed intent.

---

## The core structural claim

Ambiguity increases interpretive entropy.  
Interpretive entropy increases answer breadth (hedging).  
Answer breadth increases token consumption and reduces specificity.

ICA collapses interpretive entropy early by moving generation from **P(A|Q)** to **P(A|Q,T)** where **T** is a confirmed intent representation.

---

## Reverse Funnel hypothesis

As systems scale, user heterogeneity increases interpretive variance for ambiguous prompts. Optimisation pressure can reward broadly acceptable answers under uncertainty, leading to systematic broadening (longer, more hedged answers). ICA reverses this by narrowing interpretation before generation.

---

## What ICA does (pipeline)

1. **Ambiguity detector** estimates whether ambiguity is present *and* whether it would change the answer.
2. **Clarification selector** asks a minimal question that removes maximum uncertainty per token.
3. **Intent tag (T)** captures the confirmed definition/constraints.
4. **Answer generator** responds conditioned on (Q, T).

If ambiguity is low, the system answers immediately.

---

## Why it saves compute

For ambiguous prompts, a short clarification + a narrower conditioned answer can be cheaper than a long hedged answer.

The proposal includes a worked token model and an evaluation plan to measure:
- Total Tokens per Resolved Task (TTRT)
- Clarification trigger rate and usefulness
- Response Specificity Index (RSI)
- Agent Loop Depth Reduction (ALDR)
- Success Rate @ Budget

---

## Why it matters for agents

In coding/research agents, early ambiguity increases the branching factor of planning trees (roughly O(b^d)). Confirming constraints early can reduce branching and retries exponentially, improving completion rates under a fixed compute budget.

---

## What’s in this repo

- **ICA_Engineering_Design_Proposal_v5.pdf** — full detailed proposal (math framing, taxonomy, diagrams, token model, agent model, evaluation plan, risks, roadmap, examples)
- **diagrams/** — embedded figures used in the PDF
- **README.md** — this overview
- **LICENSE**

---

## Status

Engineering design proposal. Implementation and empirical validation are proposed in the evaluation section.
