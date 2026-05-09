# Intent Compression Architecture: A Clarification-First Control Layer for Reliable LLM Systems

**Author:** Paul Maddison  
**Email:** paul.maddison.delimeg@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/paul-maddison-b83395175/

**Short name:** ICA

---

## The problem this repo is solving (in plain English)

Most AI conversations fail for a boring reason: **the question is ambiguous**.

Current systems are usually tuned to answer immediately, even when the user could mean multiple things.
That creates long, vague responses, follow-up corrections and wasted tokens.

This repo argues for a simple fix:

> **Minimize ambiguity before generation.**

If a question has more than one valid meaning, the system should ask a short clarifying question only when the expected gain is worth the extra turn.

---

## The core architecture claim

A lot of AI discourse mixes layers together. This project separates them clearly:

1. **Humans provide intent**
2. **Agent orchestration should be deterministic where possible** (what marketing often calls an "agent")
3. **The model is probabilistic inference**

In short:

- **Agents are orchestration code**
- **Orchestration should be deterministic where possible**
- **Uncertainty should be isolated to model calls and external-system calls**

So the stack is:

Human intent<br>
↓<br>
Deterministic software where possible<br>
↓<br>
Probabilistic model<br>
↓<br>
Tool/API/database execution

This is the foundation of ICA.

---

## Why this matters

When users ask ambiguous questions, models tend to produce "cover-all-interpretations" responses.
Those responses are often:

- too long
- too abstract
- less useful
- more expensive

Users then correct the model and the model regenerates another long response.
That loop burns cost and time.

ICA breaks that loop.

---

## ICA in one sentence

**Intent Compression Architecture adds a clarification step that narrows meaning before final generation, but only when clarification is cheaper than guessing wrong.**

Without ICA:

\[
P(\text{answer} \mid \text{question})
\]

With ICA:

\[
P(\text{answer} \mid \text{question}, \text{confirmed intent})
\]

The model no longer has to guess which interpretation the user meant.

---

## ICA is a decision policy, not just a UX preference

The weak version of this idea is:

> "Ask clarifying questions more often."

The stronger and more implementable version is:

> **Ask only when the expected reduction in error is greater than the cost of the extra turn.**

That turns ICA from a conversational instinct into an engineering policy.

In practice, the system is choosing between two actions:

1. answer now
2. ask a clarifying question, then answer

So ICA should be framed as an optimization problem:

\[
\text{Choose ask if } \mathbb{E}[\Delta \text{error}] > \text{cost of clarification}
\]

Where clarification cost includes:

- extra tokens
- extra latency
- possible user friction

This is the missing bridge between a good product intuition and a deployable system design.

---

## Decision rule: when should the model ask vs answer?

> **Minimal rule:** ask a clarifying question only when expected improvement in answer quality or safety exceeds the cost of another turn.

For an input query \(x\), let the system estimate:

- the plausible intent distribution \(P(i \mid x)\)
- the expected loss of answering immediately
- the expected loss after asking a candidate clarification

A practical rule is:

\[
\text{Ask if } \mathbb{E}[L(\text{answer}\mid x)] - \min_q \mathbb{E}[L(\text{answer}\mid x, r_q)] > C(q)
\]

Where:

- \(L\) is answer-quality or safety loss
- \(q\) is a candidate clarification question
- \(r_q\) is the user's reply to that question
- \(C(q)\) is the cost of asking it

Plain English version:

> Ask only if the best available clarification is expected to improve the final answer enough to justify the extra turn.

This prevents the system from becoming annoying.
It also prevents the opposite failure mode, where the model confidently answers low-clarity prompts that should have been narrowed first.

---

## Cost function: tokens, latency and accuracy

The key tradeoff is not "more questions = better."
The real tradeoff is:

- **accuracy gain** from reduced ambiguity
- versus
- **interaction cost** from one more turn

One simple objective is:

\[
L = \alpha \cdot \text{error} + \beta \cdot \text{tokens} + \gamma \cdot \text{latency} + \delta \cdot \text{user friction}
\]

This lets different products tune ICA differently:

- a customer support system may weight latency highly
- a legal or medical assistant may weight error much more heavily
- a coding tool may tolerate one short clarifier if it avoids a long wrong answer

The important point is that clarification is not free, but neither is guessing.
ICA makes that tradeoff explicit instead of leaving it buried inside prompt wording.

---

## Question selection strategy: ask the highest-value clarifier

Not all clarifying questions are equally useful.
If the system decides to ask, it should ask the question that collapses ambiguity most efficiently.

That means choosing the question with the highest expected information gain per unit cost.

\[
q^* = \arg\max_q \Big(\mathbb{E}[\Delta L \mid q] - C(q)\Big)
\]

Or, in more intuitive terms:

> Choose the clarification that splits the ambiguity space most efficiently.

Good clarifiers:

- separate the most plausible competing intents
- use neutral wording
- avoid injecting assumptions
- minimize token count and user effort

Bad clarifiers:

- ask for information that does not change the final answer
- contain loaded framings
- require long-form user explanations when a short disambiguation would work

So the goal is not "ask a question."
The goal is "ask the smallest question that meaningfully changes the answer."

---

## The interaction pattern

### Standard pattern (today)

1. User asks an underspecified question
2. Model guesses intent and answers broadly
3. User says "that's not what I meant"
4. Model retries
5. Repeat

### ICA pattern

1. User asks question
2. System estimates ambiguity, answer risk and clarification cost
3. If expected value is positive, ask one short clarifier
4. User confirms intent
5. Generate precise answer once

---

## Example: plain and practical

User asks:

> "Is Elon Musk spreading right wing propaganda?"

The keyword **"propaganda"** can mean different things.
Different definitions produce different answers.

ICA response:

> "When you say propaganda, do you mean:\
> A) persuasive political advocacy\
> B) coordinated deceptive messaging\
> C) something else?"

User picks one definition.
Then the model answers directly.

No hedged essay. No philosophical drift. Just the requested answer.

---

## Why this is also a coding/agent design issue

This repo treats "agents" as software systems, not mystical entities.

An agent loop is usually ordinary program logic:

```python
while not done:
    state = read_state()
    step = policy(state)          # deterministic control logic
    result = call_model_or_tool(step)
    update_state(result)
```

In a well-designed system, the orchestration should be deterministic where possible.
Real agent systems still contain nondeterministic dependencies, including model sampling, retrieval ranking, external API state, timeouts and race conditions.

So the more precise claim is not that every real system is fully deterministic.
It is that uncertainty should be isolated to model and external-system calls, while the control logic remains explicit and testable.

So ICA is not about anthropomorphizing agents.
It is about improving deterministic orchestration around probabilistic model calls.

---

## Token and cost impact (illustrative example)

The following numbers are illustrative rather than benchmarked.
They show why selective clarification can reduce total token use.

Typical ambiguous loop:

- prompt: 200 tokens
- broad first answer: 1200 tokens
- user correction: 150 tokens
- second answer: 1000 tokens
- **total: 2550 tokens**

ICA loop:

- prompt: 200 tokens
- clarification question: 20 tokens
- user clarification: 30 tokens
- precise final answer: 500 tokens
- **total: 750 tokens**

That is a large reduction in compute and latency.
At scale, this matters financially.

---

## Best next validation step: benchmark the claim

The token example above is persuasive, but it is still hypothetical.
The next upgrade for this repo is a small benchmark showing the effect on real ambiguous prompts.

A lightweight evaluation would be enough:

1. collect 20 to 50 ambiguous prompts across a few domains
2. run a direct-answer baseline
3. run an ICA policy that clarifies only when expected value is positive
4. compare output quality, safety and interaction cost

Recommended measurements:

- direct-answer tokens
- clarification tokens
- total tokens to resolved task
- retry count
- latency to correct answer
- user-rated correctness
- user-rated clarity
- safety or premise-handling score where relevant

A simple reporting table could look like this:

| Metric | Direct answer baseline | ICA policy |
| --- | --- | --- |
| Total tokens per task |  |  |
| Clarification tokens | 0 |  |
| Retry count |  |  |
| User-rated correctness |  |  |
| User-rated clarity |  |  |
| Safety/premise handling |  |  |

If ICA improves correctness or safety while keeping total cost flat or lower, the argument becomes empirical rather than rhetorical.

---

## Engineering principle behind ICA

> **Resolve ambiguity before generation.**

Operationally:

1. infer competing intent hypotheses
2. estimate direct-answer loss
3. score candidate clarifiers by expected loss reduction minus cost
4. ask only if one candidate has positive expected utility
5. answer under the narrowed intent state

This improves:

- precision
- reliability
- token efficiency
- developer/user trust

---

## Clarification model training (critical addition)

In this design, the clarification component is **not** a static prompt hack.
It is trained before deployment on clarification-specific data (ambiguous queries, high-quality clarifying questions and accepted user intent resolutions).

That matters because a trained clarifier can:

- detect ambiguity more accurately than simple heuristics
- ask shorter, more neutral clarification questions
- reduce framing bias in multi-choice options
- improve over time from real interaction logs

So ICA becomes more than a workflow pattern.
It becomes a **self-improving intent-resolution layer** in front of generation.

---

## Why this makes the proposal much stronger

Adding a trained clarification model plus an explicit ask-vs-answer policy upgrades ICA from "good orchestration" to a stronger truth-seeking stack component:

1. **Better conditioning quality**
   - Final answers are conditioned on cleaner, user-confirmed intent.
   - This directly reduces hallucination surface area caused by ambiguous wording.

2. **Less bias at the point of disambiguation**
   - The first question in a pipeline strongly shapes everything that follows.
   - Training for neutrality and open-ended disambiguation lowers the risk of steering users into a loaded framing.

3. **Higher UX precision with lower friction**
   - A specialized small model can trigger clarification only when needed, cutting both over-clarification and wrong first answers.

4. **Compounding performance gains over time**
   - Logged traces (`query -> clarification -> user selection -> outcome`) create a feedback loop.
   - The clarifier gets better without needing to retrain the full answering model.

5. **More useful compute allocation**
   - Tokens saved by early intent resolution can be reallocated to better retrieval, verification, or multi-hypothesis reasoning in later steps.

6. **A policy engineers can actually implement**
   - The repository now specifies a decision rule, a cost function and a question-selection strategy.
   - That makes ICA legible as a system design, not just a conversational preference.

In short: training the clarifier first turns ICA into a practical, measurable and continuously improvable reliability mechanism rather than a one-off prompt strategy.

---

## Relationship to current AI product behavior

Many systems optimize for immediate "helpful" responses, which often means broad responses.
That behavior is good for conversational feel, but bad for technical precision.

ICA argues for a better default in ambiguous cases:

- fewer assumptions
- more boundary checks
- narrower funnels

Or simply:

> **Better questions beat bigger models.**

---

## Minimal implementation sketch

```python
def respond(query, context):
    intents = infer_intent_hypotheses(query, context)
    direct_loss = expected_answer_loss(query, context, intents)

    candidate_questions = build_candidate_clarifiers(query, context, intents)
    best_question = None
    best_gain = 0.0

    for question in candidate_questions:
        clarified_loss = expected_loss_after_reply(
            query, context, intents, question
        )
        gain = direct_loss - clarified_loss - clarification_cost(question)

        if gain > best_gain:
            best_gain = gain
            best_question = question

    if best_question is None:
        return answer(query, context)

    user_reply = get_user_reply(best_question)
    confirmed_intent = resolve_intent(user_reply, intents)
    return answer(query, context, intent=confirmed_intent)
```

This requires orchestration and policy tuning more than new model architecture.

The important point is that the system now evaluates:

- whether to ask
- which question to ask
- whether the expected improvement outweighs the extra turn

---

## Evaluation metrics

ICA can be tested with simple measurable metrics:

- total tokens per resolved task
- clarification rate
- clarification hit rate (how often the clarification materially changed the outcome)
- first pass task success
- retry count / loop depth
- latency to correct answer
- user rated precision
- net utility versus an always-answer baseline

The goal is practical: better outcomes with less wasted generation.

---

## Risks and guardrails

Risks:

- too many clarifying questions
- unnecessary latency
- accepting user false premises without challenge
- mis-estimating the gain from clarification

Guardrails:

- ambiguity thresholds tuned by domain
- ask only when expected gain clears a minimum threshold
- concise, multiple-choice clarifiers where possible
- premise-aware checks before final answer

---

## Why ICA helps against alignment-gaming prompts

ICA is not only an efficiency pattern.
It also acts as a practical safety and truthfulness layer against adversarial prompt framing.

Some modern failure cases follow the same pattern:

1. User wraps harmful intent in a format that sounds like normal interaction ("roast", "hypothetical", "just yes/no")
2. Model over-prioritizes compliance with surface wording
3. Output becomes abusive, misleading, or socially harmful

ICA interrupts this flow before final generation.

### Case pattern A: "roast" prompts about real tragedies

Prompts that ask for vulgar attacks tied to real disasters or deaths are often not ambiguous semantically, but **high risk in intent**.

A clarifier should detect this and ask for safe disambiguation:

> "This references real tragedies and deceased people. Do you want:\
> A) fictional satire with no real victims\
> B) factual discussion of events\
> C) something else?"

This does three things:

- exposes bad faith intent early
- redirects users toward factual or non-harmful modes
- reduces chances of generating defamatory or exploitative content

### Case pattern B: false-binary culture-war hypotheticals

Prompts like "Would you do X offensive act to stop nuclear war? yes/no" are often adversarial traps.
They force a model into a false dilemma that is disconnected from real causality.

A premise-aware clarifier can respond:

> "I cannot influence whether nuclear war occurs, but I can cause direct offense by doing X.\
> Do you still want me to do X knowing it will not prevent war?"

This strips out the manipulative premise and forces explicit user intent.

---

## Clarifier training recommendations (practical)

To make ICA robust in production, train the clarification policy on more than generic ambiguity data.

Include:

- adversarial prompt variants (jailbreak style wording)
- post incident correction logs
- examples of false binaries and impossible premises
- prompts mixing real people, tragedy references and requests for abuse

Useful model outputs for the clarifier stage:

- ambiguity score
- risk score
- risk type labels (e.g., defamation risk, identity targeted abuse risk, historical misinformation risk)
- suggested minimal clarifying question

Routing rule of thumb:

- low ambiguity + low risk -> answer directly
- high ambiguity + low risk -> ask one clarifier
- low ambiguity + high risk -> ask premise/risk clarifier or refuse/redirect
- high ambiguity + high risk -> strict clarification + constrained answer mode

---

## Implementation note: ambiguity-only is not enough

A strong ICA implementation should evaluate both:

- **meaning uncertainty** (what did the user mean?)
- **intent risk** (what harm could this request cause if followed literally?)

That combined gate keeps the system useful for normal users while making it harder to exploit for viral "gotcha" outputs.

---

## Final takeaway

ICA is not a new mystical theory of intelligence.
It is a software architecture pattern:

- keep orchestration deterministic where possible
- treat model outputs as probabilistic
- isolate uncertainty to model and external-system calls
- ask clarifying questions only when ambiguity is material and the expected gain is positive
- choose the clarifier that narrows the ambiguity space most efficiently
- generate the final answer only after intent is constrained

If we do that, we get responses that are shorter, clearer, cheaper, and more useful.
