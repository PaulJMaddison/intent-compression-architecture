# UCL Relationship-Intelligence Example

> **Historical example.** This shows how the old ICA idea could be used before searching relationship data. It is not the current Clarity Gateway implementation.

## Example request

```text
Prep me on Alex before the UCL partner call.
```

At first glance this sounds simple, but important details are missing.

The user could mean:

| What the user wants | Information needed | Likely result |
| --- | --- | --- |
| A meeting brief about a known contact | recent meetings, open actions, account context and decision history | summary and talking points |
| A possible introduction | mutual contacts, previous introductions and relevant relationship information | suggested introduction route |
| A risk or concern review | unresolved issues, disputed facts, escalations and gaps in evidence | caution, more evidence or human follow-up |

These are different tasks. Fetching a large pile of information before working out which task matters can waste time and can produce the wrong answer.

## The simple ICA rule

**Ask before retrieving data only when the missing information would change what you retrieve or what you do next.**

Ask first if you need to know:

- which Alex the user means
- which organisation or contact is relevant
- whether the user wants a briefing, introduction, risk review or something else
- which time period matters
- which types of source should be searched

Do **not** ask if every reasonable interpretation needs the same information.

In that case, retrieve the shared information, state the assumption clearly and continue.

## Example clarification

```text
Which Alex do you mean, and do you want a meeting brief, an introduction path or a risk review?
```

That question is useful only when the answer changes the search or the next action.

If reliable context already tells the system which Alex is on the call and what the user is trying to do, asking again would just be annoying.

## What the probability numbers mean

The old ICA format can attach probability estimates to possible meanings.

For example, because the prompt says "partner call", the system might think a meeting brief is the most likely intent.

That number is only an estimate of **what the user probably wants**. It does not prove:

- that a relationship exists
- that a person is important
- that a retrieved fact is true
- that one source should be trusted

The user's answer and the evidence found during retrieval can change those estimates.

## How this could be tested

A useful small test would compare three approaches.

### 1. Retrieve immediately

Search broadly and answer using the system's first guess about the user's meaning.

### 2. ICA before retrieval

Ask one short question only when it would change the information being retrieved or the action taken.

### 3. Retrieve immediately, then repair

Include what happens when the first route chooses the wrong person, organisation, evidence or action and the user has to correct it.

Useful measurements include:

- how often clarification changed the information retrieved
- how often the immediate route focused on the wrong person or organisation
- how often user correction changed the final action
- how often ICA asked an unnecessary question
- how much work the user had to do to correct the AI
- total tokens needed to reach the right result
- how often clarification materially changed the final answer

## What success looks like

Success does **not** mean ICA asks more questions.

Success means it asks at the right moment: before an unclear request would cause the system to retrieve the wrong information or take the wrong action, while staying out of the way when the meaning is already clear enough.
