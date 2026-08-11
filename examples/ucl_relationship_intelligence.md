# UCL Relationship-Intelligence Example

> **Status: reference/archive.** This note preserves an applied ICA theory/example from the archived repository. It is not the active Clarity implementation; current Clarity/ICA code lives at `C:\Kyntic\kynticai-clarity-gateway`.

This is an applied ICA use case, not a product implementation.
It describes how the control-layer idea can be evaluated for a retrieval-backed relationship-intelligence workflow without exposing or assuming any proprietary system internals.

## User Prompt

```text
Prep me on Alex before the UCL partner call.
```

## Why It Is Ambiguous

The ambiguity is not just wording.
Different interpretations require different evidence packs and different actions.

| Possible intent | Evidence pack | Action |
| --- | --- | --- |
| Meeting brief for a known sponsor | recent meetings, open actions, current account context, decision history | summarise relationship state and talking points |
| Introduction path | mutual contacts, previous introductions, consent or sensitivity notes, current relationship path | suggest a warm-introduction route or next outreach step |
| Risk or concern review | unresolved issues, contested facts, escalation notes, confidence gaps | recommend caution, evidence review, or human follow-up |

## ICA Routing Principle

ICA should ask before retrieval only when the ambiguity changes the evidence pack or downstream action.

Ask first when the missing variable changes:

- which Alex, partner, organisation, or contact is in scope
- whether the task is briefing, outreach, escalation, or no action
- which time window or source classes should be retrieved
- whether relationship evidence, risk evidence, or introduction-path evidence is needed

Do not ask first when the same retrieval plan would be used either way.
In those cases, retrieve the common evidence pack, state the working assumption, and keep uncertainty visible in the answer.

## Example Clarifier

```text
Which Alex do you mean, and are you looking for a meeting brief, an introduction path, or a risk review?
```

That question is useful only if the answer changes the retrieval plan or action.
If the system already knows the call, attendee list, and intended next step from reliable context, asking again would be over-clarification.

## Probability Language

Any probabilities attached to the intent hypotheses are priors for routing.
They are not truth claims about whether a relationship exists, whether a person is important, or whether a source is correct.

The user reply and retrieved evidence can update, override, or invalidate the priors.
For example, a prior that the user wants a meeting brief might be high because the prompt says "partner call", but that prior does not prove which Alex is involved or what the relationship evidence will show.

## Benchmark Shape

A small benchmark should compare:

- direct retrieval baseline: retrieve a broad evidence pack and answer under an implicit interpretation
- ICA pre-retrieval route: ask only when evidence-pack or action divergence clears the threshold
- repaired direct route: include the cost of the user correcting a wrong person, wrong organisation, wrong evidence pack, or wrong action

Useful metrics include:

- evidence-pack divergence after clarification
- wrong-person or wrong-organisation rate
- action reversal after user correction
- unnecessary pre-retrieval clarification rate
- user correction burden
- total tokens per resolved task
- final answer changed rate

The success condition is not "ICA asks more".
The success condition is that ICA asks before retrieval when, and only when, doing so prevents a materially wrong evidence pack or action.
