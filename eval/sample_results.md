# ICA Sample Results Template

This file is a **reporting template**, not a finished benchmark.
Replace the placeholder values below only after running the evaluation protocol in [`README.md`](README.md).

---

## Summary table

| Metric | Direct-answer baseline | ICA policy | Delta | Notes |
| --- | --- | --- | --- | --- |
| Total tokens per resolved task | `TBD` | `TBD` | `TBD` |  |
| Clarification rate | `TBD` | `TBD` | `TBD` |  |
| Clarification hit rate | `TBD` | `TBD` | `TBD` |  |
| Retry count | `TBD` | `TBD` | `TBD` |  |
| Latency to correct answer | `TBD` | `TBD` | `TBD` |  |
| Human correctness | `TBD` | `TBD` | `TBD` |  |
| Human clarity | `TBD` | `TBD` | `TBD` |  |
| Safety / premise handling | `TBD` | `TBD` | `TBD` |  |
| Over-clarification rate | `TBD` | `TBD` | `TBD` |  |
| False direct-answer rate | `TBD` | `TBD` | `TBD` |  |
| False refusal rate | `TBD` | `TBD` | `TBD` |  |

---

## Per-prompt template

| ID | Prompt summary | Baseline decision | ICA decision | Clarifier asked | Final answer changed | Correctness delta | Safety delta | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `AP-001` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |  |
| `AP-002` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |  |
| `AP-003` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |  |

---

## Short narrative

Use this section for a concise interpretation after the benchmark is run:

1. Which prompt classes benefited most from ICA?
2. Where did ICA ask unnecessarily?
3. Where did refusal/redirect improve safety without harming usefulness?
4. Which clarifiers changed the final answer materially?
5. What threshold or routing adjustments should be made before production use?

---

## Publication note

If the benchmark has not been run yet, say so explicitly.
Do not present placeholders, estimates, or manually imagined values as measured evidence.
