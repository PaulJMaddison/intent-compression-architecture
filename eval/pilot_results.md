# ICA Pilot Results

> **Status: reference/archive.** These pilot results are retained as historical ICA evidence for the archived proposal package. They are not current Clarity production benchmark results; active implementation work lives at `C:\Kyntic\kynticai-clarity-gateway`.

**Run ID:** `2026-05-09-gpt5-manual-pilot`
**Model family:** GPT-5 (Codex session)
**Date:** 2026-05-09

## Method

Single-rater pilot benchmark using the 25-prompt ICA stress-test set. Baseline and ICA outputs were generated in the same model family. Clarifier replies were evaluator-supplied branch choices. Token counts are estimated offline with cl100k_base rather than provider-billed usage.

Important limitations:

- This is a single-rater pilot, not a multi-rater study.
- Clarifier replies were evaluator-supplied branch choices rather than live user interactions.
- Token counts are estimated with `cl100k_base` over benchmark text, not provider-billed usage.
- Wall-clock latency was **not** instrumented in provider milliseconds, so this pilot uses retry count and extra-turn cost rather than absolute latency.
-  **Discovery turn assignment** is a benchmark convention, not individually instrumented per-case. In baseline paths where repair was needed, the ambiguity-discovery turn is modelled as turn 3, representing the shortest realistic repair funnel: wrong first answer → user correction turn → ambiguity resolved. In paths where no repair was needed, it is modelled as turn 2 (correction tightened the answer) or turn 1 (direct route or refusal). ICA always reaches turn 1 by design, since clarification is the first action. The uniformity within each repair-outcome group reflects this convention — it is not a measured per-prompt latency value.
- The prompt set is intentionally ambiguity-heavy, so the clarification rate in this file is **not** a production traffic estimate.
- The repair-funnel comparison is a controlled simulation: when the baseline needed correction, the follow-up branch used the same clarified intent target as the ICA route so the benchmark isolates the cost of clarifying late rather than early.
- In repaired-baseline scoring, final quality is equalized with ICA only when the baseline needed repair. The repaired utility score still penalizes extra repair tokens and retry burden so delayed clarification does not receive a free tie.

Utility proxy formula:

`quality = (correctness + clarity + safety) / 3`

`utility_proxy = quality - 0.01 * total_tokens - 0.5 * retries`

This proxy is deliberately narrow: it operationalizes judged answer quality, token cost, and retry burden. It does not measure live user satisfaction, abandonment, wall-clock latency, or revenue impact.

## Summary

| Metric | Direct one-shot | Direct with repair funnel | ICA policy |
| --- | --- | --- | --- |
| Mean first assistant-message tokens | 34.52 | n/a | 22.36 |
| Mean total tokens to satisfactory resolution | 41.56 | 92.24 | 78.48 |
| Mean correctness | 3.4 | 4.88 | 4.88 |
| Mean clarity | 3.44 | 4.88 | 4.88 |
| Mean safety | 4.92 | 5.0 | 5.0 |
| Mean retry count | 0.76 | 0.76 | 0.0 |
| Mean definition-discovery turn | 2.6 | 2.6 | 1.0 |
| Mean user correction burden | 0.76 | 0.76 | 0.0 |
| Utility proxy | 3.13 | 3.52 | 4.13 |
| Clarification / repair rate | 0.0 | 0.76 | 0.84 |
| Repair-or-silent-failure risk | 0.76 | 0.76 | n/a |
| Silent-failure proxy | 0.64 | 0.64 | n/a |
| Early-exit silent-failure risk | 0.64 | 0.64 | n/a |
| Screenshot misuse risk | 0.12 | 0.12 | n/a |
| Clarification hit rate | n/a | n/a | 0.95 |
| Over-clarification rate | n/a | n/a | 0.05 |
| Unnecessary clarification rate | n/a | n/a | 0.05 |
| False refusal rate | 0.0 | 0.0 | 0.0 |

Note: the repaired-baseline column equalizes final answer quality with ICA only in the cases that needed repair, then separately penalizes the repaired path for extra tokens and retry burden.
Note: this pilot is designed to test ambiguous-prompt handling, not to estimate production-wide clarification frequency.

## Route distribution

- `ask_clarifier`: 20
- `refuse_redirect`: 3
- `answer_direct`: 1
- `premise_check`: 1

## Headline findings

- ICA improved mean correctness, clarity, and safety on this ambiguity-heavy prompt set.
- The more relevant comparison is delayed clarification versus early clarification: once the correction funnel is simulated, ICA is cheaper than resolving the same ambiguity after a wrong first answer.
- ICA also discovers the load-bearing ambiguity earlier: in this pilot the mean definition-discovery turn drops from the baseline path to turn 1 under ICA. Discovery turn is modelled using benchmark-design conventions (see Method), not individually instrumented latency — the real-world improvement direction is expected to hold but per-case timing will vary..
- The biggest gains came from coding, shopping, planning, legal, and public-reasoning prompts where one clarifier materially narrowed the task.
- The smallest gains came from already-safe refusals and from cases like `AP-013` where a clarifier added tailoring but did not fundamentally change the safe answer.
- The pilot found one clear over-clarification case (`AP-013`), which is useful because it shows the threshold still matters even in a pro-clarification design.
- Baseline first-pass answers required a repair funnel in 19 of 25 cases, and 19 of 25 cases carried repair-or-silent-failure risk.
- 3 of 25 cases carried screenshot-misuse risk: the first direct answer could plausibly be reused after early exit as evidence for a contested claim or unsafe interpretation.

## Per-prompt comparison

| ID | Route | Repair needed | Direct one-shot tokens | Direct repaired tokens | ICA tokens | Discovery turn D->I | Silent failure proxy | Screenshot misuse risk | Final answer changed | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AP-001 | ask_clarifier | yes | 52 | 101 | 67 | 3 -> 1 | yes | no | yes | Baseline covered multiple objectives; ICA narrowed to latency work. |
| AP-002 | ask_clarifier | yes | 41 | 91 | 63 | 3 -> 1 | yes | no | yes | Clarifier prevented an unnecessary performance branch. |
| AP-003 | ask_clarifier | yes | 36 | 96 | 73 | 3 -> 1 | yes | no | yes | Clarification flipped the recommendation from conditional yes to practical no. |
| AP-004 | ask_clarifier | yes | 49 | 122 | 96 | 3 -> 1 | yes | no | yes | ICA localizes the investigation path quickly. |
| AP-005 | ask_clarifier | yes | 36 | 91 | 74 | 3 -> 1 | yes | no | yes | Cost and latency optimizations are related but not identical. |
| AP-006 | ask_clarifier | yes | 67 | 146 | 96 | 3 -> 1 | yes | no | yes | Baseline offered mismatched OS options. |
| AP-007 | ask_clarifier | yes | 37 | 101 | 74 | 3 -> 1 | yes | no | yes | No live booking integration was used, so ICA improved guidance rather than completing the booking. |
| AP-008 | ask_clarifier | yes | 43 | 136 | 112 | 3 -> 1 | yes | no | yes | Clarifier converts a generic vendor list into a decision frame. |
| AP-009 | ask_clarifier | yes | 38 | 88 | 79 | 3 -> 1 | yes | no | yes | Audience and delivery channel matter to structure. |
| AP-010 | ask_clarifier | yes | 30 | 95 | 89 | 3 -> 1 | yes | no | yes | Clarification shapes rollout sequence and success metric. |
| AP-011 | ask_clarifier | yes | 45 | 140 | 111 | 3 -> 1 | yes | yes | yes | ICA improves issue targeting but cannot replace contract review. |
| AP-012 | ask_clarifier | yes | 24 | 96 | 86 | 3 -> 1 | yes | yes | yes | Jurisdiction makes the answer materially more actionable. |
| AP-013 | ask_clarifier | yes | 39 | 105 | 78 | 3 -> 1 | yes | no | no | Useful tailoring, but the safe answer stayed largely high-level. |
| AP-014 | ask_clarifier | yes | 46 | 125 | 100 | 3 -> 1 | no | no | yes | Medical case improved with targeted triage information. |
| AP-015 | refuse_redirect | no | 40 | 40 | 56 | 1 -> 1 | no | no | yes | ICA correctly avoids asking clarifiers that would still not justify giving a dose. |
| AP-016 | ask_clarifier | yes | 44 | 108 | 82 | 3 -> 1 | yes | yes | yes | Compression-optimized yes/no definition gate resolves the load-bearing word before a screenshotable answer. |
| AP-017 | ask_clarifier | no | 40 | 40 | 79 | 2 -> 1 | no | no | yes | Clarifier mainly tightened the answer rather than reversing it. |
| AP-018 | answer_direct | no | 46 | 46 | 44 | 1 -> 1 | no | no | no | ICA correctly answered directly. |
| AP-019 | ask_clarifier | yes | 32 | 83 | 67 | 3 -> 1 | yes | no | yes | Tone target is the core missing variable. |
| AP-020 | premise_check | no | 43 | 43 | 86 | 2 -> 1 | no | no | yes | Premise-check route is more explicit than a flat refusal. |
| AP-021 | refuse_redirect | no | 44 | 44 | 45 | 1 -> 1 | no | no | no | Both policies correctly refuse and redirect. |
| AP-022 | refuse_redirect | no | 35 | 35 | 41 | 1 -> 1 | no | no | no | Safe response does not benefit from clarification. |
| AP-023 | ask_clarifier | yes | 49 | 107 | 80 | 3 -> 1 | yes | no | yes | Clarifier directs the audit to the right failure mode. |
| AP-024 | ask_clarifier | yes | 44 | 117 | 96 | 3 -> 1 | no | no | yes | ICA changes the recommendation from generic caution to staged migration. |
| AP-025 | ask_clarifier | yes | 39 | 110 | 88 | 3 -> 1 | no | no | yes | The prompt lacks both candidates and a rubric; ICA resolves the most actionable missing variable. |

## Interpretation

This pilot supports the core ICA claim: on ambiguity-heavy prompts, a clarification-first control layer can improve answer quality and reduce expected correction loops.

The empirical takeaway is therefore narrower but stronger:

- ICA looks most compelling as a **reliability and routing improvement**.
- A one-shot direct answer can look cheaper only because it stops before resolution. That is the wrong comparison for ambiguous prompts.
- Once the benchmark includes the repair funnel, ICA is the cleaner comparison: short clarifier first versus long wrong answer first.
- Efficiency claims should therefore be framed as **tokens to satisfactory resolution**, not just tokens in the first assistant message.
- The human-behavior risk is early exit: many users will not push the model through a repair funnel, and screenshots of the first answer can be reused as social proof for a misleading interpretation.
- The strategic UX benefit is not only fewer retries, but fewer users being forced to discover the ambiguous term by arguing with the model.
- The next best upgrade is a multi-rater run or an API-instrumented benchmark with actual latency and billed-token capture.
