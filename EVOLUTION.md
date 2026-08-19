# From ICA to Clarity Gateway

This document is the chronology for the repository. It explains what changed, why it changed, and which ideas survived into the later Clarity Gateway direction without pretending that this archived package is the active implementation.

The sequence below is grounded in the repository's commit history and release notes. The purpose is provenance, not retrospective marketing.

## 1. The original problem: unresolved intent

The early work focused on a common LLM failure mode: the model answers an ambiguous question under one implicit interpretation, and the real disagreement appears only after one or more repair turns.

On 9 May 2026 the repository added a pilot benchmark and then rapidly refined it around correction funnels, wrong-funnel analysis, silent failure, and human early-exit behaviour:

- [`62c2e41`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/62c2e41d28419329b084b50c5d44c6ef5987e032) — pilot benchmark results
- [`8b99c01`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/8b99c018bb4d2c73401981643ac1cf9322cf6f8e) — correction-funnel modelling
- [`030200c`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/030200cf2dc24f47747fafb1c384d690347b977b) — flywheel and wrong-funnel analysis
- [`f546972`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/f546972eaa29430f8391f91aeed80366fb3332f2) — mathematical and benchmark presentation

The key shift was from “ask more clarifying questions” to a sharper engineering problem: **how do we decide whether the expected value of resolving intent is greater than the cost of another turn?**

## 2. Reproducibility before live integrations

The next step made the thesis replayable locally. Validation notes, dependencies, helper scripts and a pinned artefact toolchain were added before live provider adapters:

- [`571e64d`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/571e64dd6b69be8130b7258cca5d64a68cafd4b6) — validation and reproduction notes
- [`05dee7d`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/05dee7d2a36b9c2001e68209902a3dd5f3032307) — requirements and proposal synchronisation
- [`6868bf8`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/6868bf8a664f021fa4241ac7781e2dcddeaf3eb3) — quick start and pinned dependencies
- [`e07cc5b`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e07cc5b73a7a77d17ef57cc9a77e08b582f821ad) — local validation made canonical
- [`cde5e00`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/cde5e00af17c2f0d65488d080ce3ab9b62a7deaf) — local validation helpers
- [`e096e81`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e096e8149e046d127c8777d424293b58060764ea) — GitHub Actions schema validation deliberately removed

That decision is important to preserve. This archive does not need a modern CI badge to rewrite its history; the canonical path was intentionally local and offline.

## 3. From proposal to reusable control layer

On 12 May 2026, `ica-core` v0.1.0 made the design executable:

- [`e59064f`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e59064fff6b7db036dc495276efbe81c3f506516) — `ica-core` v0.1.0

The package established a pattern that remained central to the later Clarity direction:

- a provider boundary for probabilistic analysis
- Pydantic models for a structured decision contract
- deterministic ask/answer/premise/refusal policy code
- an offline mock provider
- CLI and test harnesses
- privacy-conscious tracing
- explicit strict and fallback behaviour

The architecture separated **estimation** from **routing**. A provider could estimate hypotheses, ambiguity, risk and clarifier utility; deterministic software could still own the final control decision.

## 4. ICA v1.0: expected utility becomes the centre

The v1.0 release and surrounding commits consolidated the project around the rule:

`ask iff max_q U(q | x) > tau`

Relevant milestones:

- [`3d70f58`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/3d70f584bf6d21dbacff00b1ae05d518f14c6472) — utility and calibration signals
- [`e534c18`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e534c18165e745b3e8e3e24c753b1b4c7814366f) — ICA v1.0.0

The important idea was not a particular threshold value. It was that the cost of clarification, the cost of a wrong answer, latency, token use, friction and safety risk could be made explicit control variables rather than left to conversational style.

## 5. The agentic turn

Immediately after v1.0, the repository broadened the thesis from chat clarification to agent reliability:

- [`cc3435b`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/cc3435bb59adf396edc4239e3cf2041f3c17c42e) — coding-agent task-state bridge
- [`6beb312`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/6beb312ef7155a8468173d8490bd722af28c293e) — intent control-plane positioning
- [`e70332a`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e70332a60fe6f4b88123e08818273fd98c6e8ec0), [`d819033`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/d819033fb3d3e5d9bc19b9f5a3ba251721ba58ef), [`25cdf6b`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/25cdf6b55952067c97703c9c8262ee0f16feada2) — increasingly explicit agentic framing

The compressed object was no longer only “what did the user mean?” It became a compact packet such as:

```text
original user goal
current verified state
known constraints
failed attempts to avoid
next best action
```

This was the conceptual bridge from clarification UX to a **Clarity Gateway**: a boundary that keeps intent, state and action aligned before expensive or irreversible work happens.

## 6. Benchmark refinement rather than benchmark inflation

On 13 May, the pilot material was corrected to clarify how the definition-discovery turn was modelled:

- [`950b635`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/950b635e71bf0c03542d436f5746ea4620707a8e) — discovery-turn clarification

That matters because this archive is most useful when it preserves caveats. The pilot is evidence about the design and measurement approach, not a universal production performance claim.

## 7. Applied retrieval and relationship intelligence

On 16 June the UCL example applied the control-plane idea to retrieval-backed work:

- [`a582f77`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/a582f7716a1f3010f65cdc74153953ebc294eb85) — UCL relationship-intelligence ICA example

The important extension was: **clarify before retrieval only when the ambiguity changes the evidence pack or downstream action**. If every plausible intent uses the same evidence, retrieve first and keep the assumption visible. If intent changes person, scope, source set, relationship type or action, clarification can save a much larger wrong-funnel cost.

## 8. Transition from active idea to reference lineage

The repository was explicitly marked as an archive on 16 June:

- [`04f2d7c`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/04f2d7c4f336289ab57ca8afd0cf93e33b216f4c) — archive state

Later commits aligned source-of-truth routing and repository identity:

- [`4b1c311`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/4b1c3111564817d1ba8f03deb9a0821bc237fb5f) — archive source-of-truth routing
- [`9fb9f2c`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/9fb9f2cefa53ee5c5d87a162cd9761acfdcf56b4) — repository identity alignment
- [`cc18147`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/cc18147021732ba1f1b49e46ebe06a0265a92862) — mandatory Git safety rules

The archive hardening that followed keeps the executable reference healthy while making that boundary public and machine-independent.

## Concepts that persisted into the Clarity Gateway direction

The historical record shows a consistent set of ideas becoming more general over time:

- resolve **load-bearing ambiguity** before committing to an answer or action
- keep ambiguity, risk and premise validity separate
- use model estimates as inputs, not unquestioned truth
- prefer deterministic orchestration where deterministic software can own the decision
- make control decisions structured and observable
- calibrate thresholds from outcomes rather than taste
- measure total cost to resolved intent, not only first-response token count
- preserve original task intent and verified state in long-running agents
- treat retrieval scope and downstream action as part of the cost of misunderstanding

Those ideas are the reason this repository is worth preserving.

## What not to infer

The archive does **not** claim that current Clarity Gateway internals, naming, schemas, providers, benchmarks or commercial evidence are identical to this repository. It documents the lineage. Current implementation truth belongs to the active product repositories and documentation, not to a historical snapshot.
