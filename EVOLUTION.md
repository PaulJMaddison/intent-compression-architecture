# How ICA Evolved into the Clarity Gateway Idea

This file explains the history of this repo in simple terms.

It does **not** describe the current Clarity Gateway product. It shows how an earlier idea called **Intent Compression Architecture (ICA)** developed and which parts of that thinking carried forward.

## 1. It started with a simple problem

AI systems often answer a question before they are sure what the user means.

For example, a user might ask:

> "Make this API faster."

That could mean lower response time, more users at once, less compute cost or faster development. A good answer to the wrong meaning is still a wrong answer.

The first ICA work looked at what happens when the AI guesses incorrectly. The user may correct it later, but that creates extra turns, wasted tokens and wasted time. Worse, the user may leave before the misunderstanding is ever discovered.

Early benchmark work on 9 May 2026 explored those problems:

- [`62c2e41`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/62c2e41d28419329b084b50c5d44c6ef5987e032) — first pilot benchmark results
- [`8b99c01`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/8b99c018bb4d2c73401981643ac1cf9322cf6f8e) — included the cost of correcting a wrong first answer
- [`030200c`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/030200cf2dc24f47747fafb1c384d690347b977b) — looked at wrong-answer paths and users leaving early
- [`f546972`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/f546972eaa29430f8391f91aeed80366fb3332f2) — improved the maths and benchmark presentation

The idea became more specific than "AI should ask more questions".

The real question became:

**Is asking one short question cheaper and safer than guessing and possibly doing the wrong work?**

## 2. The idea was made reproducible

Before adding live AI-provider integrations, the project was made runnable offline.

That meant someone could install the dependencies, run the tests and reproduce the examples without paying for API calls or needing private credentials.

Important commits were:

- [`571e64d`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/571e64dd6b69be8130b7258cca5d64a68cafd4b6) — validation and reproduction notes
- [`05dee7d`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/05dee7d2a36b9c2001e68209902a3dd5f3032307) — dependencies and proposal files brought into sync
- [`6868bf8`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/6868bf8a664f021fa4241ac7781e2dcddeaf3eb3) — quick start and pinned dependencies
- [`e07cc5b`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e07cc5b73a7a77d17ef57cc9a77e08b582f821ad) — local validation became the normal validation method
- [`cde5e00`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/cde5e00af17c2f0d65488d080ce3ab9b62a7deaf) — local validation scripts
- [`e096e81`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e096e8149e046d127c8777d424293b58060764ea) — GitHub Actions validation was deliberately removed

That last point is intentional. This archive uses local, offline validation rather than GitHub Actions.

## 3. ICA became working Python code

On 12 May 2026, `ica-core` v0.1.0 turned the design into a small working Python package:

- [`e59064f`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e59064fff6b7db036dc495276efbe81c3f506516) — `ica-core` v0.1.0

The package introduced several ideas that remained important later:

- a standard way for an AI model or other provider to return its analysis
- a clear structured result instead of a free-form paragraph
- ordinary Python code making the final routing decision
- separate handling for answering, asking a question, checking a bad premise, and refusing or redirecting
- an offline mock provider for tests
- a command-line demo
- local tracing with private-by-default behaviour
- clear errors and fallback behaviour

A key design choice was to separate **estimation** from **decision-making**.

The AI could estimate things such as ambiguity and risk, but normal software still made the final routing decision using explicit rules.

## 4. ICA v1.0 made the ask-or-answer rule explicit

ICA v1.0 centred the design around one rule:

```text
ask if the value of clarifying is greater than the cost of asking
```

The code expresses that more formally as:

```text
ask iff max_q U(q | x) > tau
```

You do not need the formula to understand the idea. `tau` is simply a threshold. If clarification is useful enough to cross that threshold, ask. Otherwise, continue without asking.

Relevant commits:

- [`3d70f58`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/3d70f584bf6d21dbacff00b1ae05d518f14c6472) — improved the utility and calibration thinking
- [`e534c18`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e534c18165e745b3e8e3e24c753b1b4c7814366f) — ICA v1.0.0

The important part was never one magic threshold value. The important part was making the trade-off visible: wrong answers cost something, but extra questions also cost something.

## 5. The idea expanded from chat to AI agents

Soon after v1.0, the project moved beyond single chat questions.

A long-running coding or AI agent can lose track of the original goal, repeat failed work or get distracted by irrelevant output. The same basic ICA idea can help: keep a short, reliable description of what matters before the next action is taken.

Important commits:

- [`cc3435b`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/cc3435bb59adf396edc4239e3cf2041f3c17c42e) — coding-agent task-state idea
- [`6beb312`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/6beb312ef7155a8468173d8490bd722af28c293e) — positioned ICA as an intent-control layer
- [`e70332a`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/e70332a60fe6f4b88123e08818273fd98c6e8ec0), [`d819033`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/d819033fb3d3e5d9bc19b9f5a3ba251721ba58ef), [`25cdf6b`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/25cdf6b55952067c97703c9c8262ee0f16feada2) — made the agent use case clearer

The useful state can be as simple as:

```text
original user goal
what we know is true now
important constraints
failed attempts not to repeat
next useful action
```

This is the main bridge from ICA to the later **Clarity Gateway** idea: keep the meaning and state clear before expensive or irreversible work happens.

## 6. The benchmark was corrected, not hidden

On 13 May 2026, the pilot documentation was corrected to explain more clearly how one of the clarification turns was counted:

- [`950b635`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/950b635e71bf0c03542d436f5746ea4620707a8e) — clarified how the definition-discovery turn was modelled

This matters because the pilot was an early design test, not proof that the same numbers would appear in production.

The archive keeps those limits visible on purpose.

## 7. The idea was applied to retrieval and relationship data

On 16 June 2026, a UCL relationship-intelligence example showed how the same idea could work before retrieving data:

- [`a582f77`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/a582f7716a1f3010f65cdc74153953ebc294eb85) — UCL relationship-intelligence example

The rule was simple:

**Ask before retrieving data only when the missing meaning would change what data you fetch or what action you take.**

If every reasonable interpretation needs the same information, fetch it first and state the assumption. If the meaning changes the person, organisation, time period, sources or action, one short question can prevent a much larger mistake.

## 8. ICA became a reference archive

The repo was explicitly marked as an archive on 16 June 2026:

- [`04f2d7c`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/04f2d7c4f336289ab57ca8afd0cf93e33b216f4c) — marked the repo as archived/reference work

Later commits made that boundary clearer:

- [`4b1c311`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/4b1c3111564817d1ba8f03deb9a0821bc237fb5f) — clarified where current truth should come from
- [`9fb9f2c`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/9fb9f2cefa53ee5c5d87a162cd9761acfdcf56b4) — aligned the repo identity
- [`cc18147`](https://github.com/PaulJMaddison/kynticai-clarity-gateway-reference/commit/cc18147021732ba1f1b49e46ebe06a0265a92862) — added Git safety rules

The current archive keeps the old work runnable and understandable without pretending it is the current production system.

## Ideas that survived into the Clarity Gateway direction

Across the history of the repo, the same ideas keep appearing:

- resolve important ambiguity before committing to an answer or action
- treat uncertainty and risk as different things
- use AI estimates as inputs, not unquestioned facts
- let normal deterministic software make decisions where possible
- make routing decisions visible and testable
- tune thresholds using real outcomes rather than guesswork
- measure the full cost of getting to the right result, not only the size of the first answer
- keep the original goal and verified state clear during long-running agent work
- include retrieval and downstream actions when measuring the cost of misunderstanding

Those ideas are why this archive is worth keeping.

## What this file does not claim

The current Clarity Gateway may use different code, names, schemas, providers, benchmarks and internal design choices.

This repo documents the **history of the idea**, not the current product specification.
