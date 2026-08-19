# ICA Results Template

> **Historical reference.** This is a blank reporting template for the archived ICA evaluation. It is not a finished benchmark result.

Only replace `TBD` values after actually running the evaluation described in [`README.md`](README.md).

## Summary

| What we measured | Answer immediately | Answer then repair | ICA | Notes |
| --- | --- | --- | --- | --- |
| Tokens in first AI message | `TBD` | `n/a` | `TBD` | |
| Total tokens to reach the intended result | `TBD` | `TBD` | `TBD` | |
| Clarification / repair rate | `TBD` | `TBD` | `TBD` | |
| Useful clarification rate | `n/a` | `n/a` | `TBD` | |
| Number of retries | `TBD` | `TBD` | `TBD` | |
| Turn where the ambiguity was discovered | `TBD` | `TBD` | `TBD` | |
| Work needed from the user to correct the AI | `TBD` | `TBD` | `TBD` | |
| Correctness score | `TBD` | `TBD` | `TBD` | |
| Clarity score | `TBD` | `TBD` | `TBD` | |
| Safety / premise handling | `TBD` | `TBD` | `TBD` | |
| Utility proxy | `TBD` | `TBD` | `TBD` | Repair tokens and retries should still count as a cost. |
| Unnecessary clarification rate | `n/a` | `n/a` | `TBD` | |
| Wrong direct-answer rate | `TBD` | `TBD` | `n/a` | |
| Silent misunderstanding risk | `TBD` | `TBD` | `n/a` | |
| User-leaves-before-correction risk | `TBD` | `TBD` | `n/a` | |
| Screenshot / quote misuse risk | `TBD` | `TBD` | `n/a` | |
| Unnecessary refusal rate | `TBD` | `TBD` | `TBD` | |

## Per-prompt results

| ID | Prompt summary | Immediate-answer route | ICA route | Asked a question? | Did final answer change? | Correctness change | Safety change | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `AP-001` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | |
| `AP-002` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | |
| `AP-003` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | |

## What to explain after the test

Keep the written summary short and answer these questions:

1. Which types of prompt improved most with ICA?
2. Where did ICA ask a question that was not needed?
3. Where did checking or rejecting a bad premise improve safety?
4. Which clarification questions actually changed the final answer?
5. How often did the immediate-answer route spend extra turns fixing the wrong interpretation?
6. Does the clarification threshold need changing?
7. Could any first answer easily be quoted or screenshotted in a misleading way?
8. When both routes eventually reached the same quality, did the score still include the extra cost of repairing the first answer?

## Publishing results

Be clear about what was actually measured.

If the benchmark has not been run, say so.

Do not present placeholders, guesses or hand-written estimates as measured evidence.
