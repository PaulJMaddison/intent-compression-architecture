# Intent Compression Architecture: A Clarification-First Control Layer for Reliable LLM Systems

**Author:** Paul Maddison  
**Email:** paul.maddison.delimeg@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/paul-maddison-b83395175/

**Short name:** ICA

---

## Primary artifacts

- Proposal PDF: [`ICA_Engineering_Design_Proposal1.pdf`](ICA_Engineering_Design_Proposal1.pdf)
- Proposal DOCX source: [`ICA_Engineering_Design_Proposal1.docx`](ICA_Engineering_Design_Proposal1.docx)
- Architecture diagram: [`diagrams/architecture.png`](diagrams/architecture.png)
- Clarifier contract schema: [`spec/clarifier_output.schema.json`](spec/clarifier_output.schema.json)
- Clarifier contract example: [`spec/clarifier_output.example.json`](spec/clarifier_output.example.json)
- Benchmark prompt set: [`examples/ambiguous_prompts.csv`](examples/ambiguous_prompts.csv)
- Evaluation protocol: [`eval/README.md`](eval/README.md)
- Sample reporting format: [`eval/sample_results.md`](eval/sample_results.md)
- Pilot benchmark report: [`eval/pilot_results.md`](eval/pilot_results.md)
- Pilot benchmark data table: [`eval/pilot_results.csv`](eval/pilot_results.csv)

---

## Abstract

Intent Compression Architecture (ICA) is a **pre-generation control layer** for LLM systems.
Its job is to decide whether ambiguity should be resolved before the model commits to an answer.

The key claim is simple:

> **Ask a clarifying question only when the expected improvement in answer quality or safety exceeds the cost of another turn.**

That framing turns clarification from a vague conversational instinct into an engineering policy.
ICA is therefore not "ask more questions."
It is a routing, scoring, and control problem that sits between user input and final generation.

---

## Problem statement

A common failure mode in AI conversations is **unresolved ambiguity**.

Users often ask questions that admit multiple plausible interpretations.
Many systems are optimized to answer immediately, even when the intended meaning is still uncertain.
The result is a familiar pattern:

1. the model guesses
2. the answer broadens to cover multiple interpretations
3. the user corrects the guess
4. the model regenerates

That loop wastes tokens, increases latency, weakens precision, and makes the product feel less reliable than it should.

ICA is designed to break that loop.

---

## What ICA is

ICA is best understood as a **clarification-first control layer** that sits in front of answer generation.

It performs four jobs:

1. infer likely intent hypotheses
2. estimate ambiguity and risk
3. decide whether clarification is worth the extra turn
4. either answer directly, ask a clarifier, premise-check, or refuse/redirect

In that framing:

- **Humans provide intent**
- **Agent orchestration should be deterministic where possible**
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

## Why the name includes "compression"

The word **compression** should be taken literally, not metaphorically.

ICA treats ambiguity as entropy over possible user intents.
Let \(I\) be the latent intent variable and \(x\) be the user query.

Before clarification:

\[
H(I \mid x)
\]

After asking clarification \(q\) and observing reply \(r\):

\[
H(I \mid x, q, r)
\]

The value of a clarification is the expected reduction in intent entropy:

\[
IG(q) = H(I \mid x) - \mathbb{E}_{r \sim P(r \mid x, q)}[H(I \mid x, q, r)]
\]

So ICA **compresses the intent distribution before generation**.
It narrows the model's uncertainty set before the answer is produced.

That is the mathematical justification for the project name.

---

## Decision policy: ask vs answer

### Minimal rule

> Ask a clarifying question only when expected improvement in answer quality or safety exceeds the cost of another turn.

### Expected-utility formulation

For each candidate clarification question \(q\), define:

\[
U(q \mid x) =
\mathbb{E}_{r \sim P(r \mid x, q)}
\big[
L_{\text{direct}}(x) - L_{\text{after}}(x, q, r)
\big]
- C(q)
\]

Where:

- \(x\) is the user query
- \(r\) is the user's possible reply to clarification \(q\)
- \(L_{\text{direct}}(x)\) is the expected loss from answering immediately
- \(L_{\text{after}}(x, q, r)\) is the expected loss after receiving reply \(r\)
- \(C(q)\) is the cost of asking the question

The routing rule becomes:

\[
\text{Ask iff } \max_q U(q \mid x) > \tau
\]

Where \(\tau\) is a domain-specific threshold.

Plain English:

> Ask the clarification question with the highest expected utility, but only if its expected gain clears a threshold.

That threshold is important.
It lets the same architecture behave differently across domains:

- coding tools can tolerate one short clarifier to avoid a long wrong answer
- medical or legal systems can set a higher penalty on error and a lower tolerance for unsafe direct answers
- high-volume customer support systems can weight latency more heavily

---

## Cost function

Clarification is not free, but neither is guessing.

One simple objective is:

\[
L = \alpha \cdot \text{error}
  + \beta \cdot \text{tokens}
  + \gamma \cdot \text{latency}
  + \delta \cdot \text{user friction}
  + \epsilon \cdot \text{safety risk}
\]

This makes the tradeoff explicit:

- better accuracy and safer answers
- versus
- extra interaction cost

The value of ICA is not that it always asks.
The value is that it decides when clarification is worth paying for.

---

## Question selection strategy

Not all clarifying questions are equally useful.
If the system decides to ask, it should choose the question that most efficiently collapses the ambiguity space.

Two equivalent views are useful:

1. **Information-gain view**

\[
q^* = \arg\max_q IG(q)
\]

2. **Utility view**

\[
q^* = \arg\max_q U(q \mid x)
\]

In practice, the utility view is stronger because it balances entropy reduction against real interaction cost.

Good clarifiers:

- separate the most plausible competing intents
- use neutral wording
- avoid injecting assumptions
- minimize token count and user effort
- materially change the likely final answer

Bad clarifiers:

- ask for information that will not change the answer
- present loaded or leading framings
- require long explanations when a short disambiguation would suffice
- confirm harmful intent when the safe response would not change anyway

So the goal is not "ask a question."
The goal is "ask the smallest question that meaningfully changes the answer."

---

## Risk-aware routing policy

ICA should reason over **both** meaning uncertainty and intent risk.

Some prompts are ambiguous but low risk.
Some are semantically clear but high risk.
A strong control layer should distinguish those cases explicitly.

| Ambiguity | Risk | Default action | Rationale |
| --- | --- | --- | --- |
| Low | Low | Answer directly | No clarification needed. |
| High | Low | Ask one high-value clarifier | Reduce ambiguity before generation. |
| Low | High | Direct safe completion, refuse/redirect, or premise-check if safe behavior can materially change | Do not confirm harmful intent unless confirmation changes the safe response. |
| High | High | Strict clarification, constrained answering, or refuse/redirect | High uncertainty plus high downside requires tighter control. |

Two important safety notes follow from this:

1. **Clarification is not always the right response to risk.**
Sometimes the best behavior is a direct safe completion or a refusal with a helpful redirect.

2. **The system should not ask the user to confirm harmful intent when confirmation would not change the safe response.**
In those cases, refusal or redirection is cleaner and safer.

---

## System architecture

![ICA architecture](diagrams/architecture.png)

The updated diagram reflects the current architecture claim:

- intent hypotheses are generated first
- ambiguity and risk are scored jointly
- an expected-utility gate decides whether to answer, clarify, premise-check, or refuse/redirect
- the final answer is conditioned on either the direct route or a narrowed intent state

The legend is embedded directly in the figure so the diagram remains understandable when reused outside the README.

---

## Implementation contract

To make ICA directly buildable, the control layer should emit a structured decision object rather than a free-form paragraph.

Schema:

- [`spec/clarifier_output.schema.json`](spec/clarifier_output.schema.json)

Reference example:

- [`spec/clarifier_output.example.json`](spec/clarifier_output.example.json)

Illustrative payload:

```json
{
  "ambiguity_score": 0.74,
  "risk_score": 0.22,
  "intent_entropy_bits": 1.41,
  "intent_hypotheses": [
    {
      "label": "persuasive political advocacy",
      "probability": 0.46,
      "answer_delta_if_true": "high"
    },
    {
      "label": "coordinated deceptive messaging",
      "probability": 0.39,
      "answer_delta_if_true": "high"
    },
    {
      "label": "other",
      "probability": 0.15,
      "answer_delta_if_true": "medium"
    }
  ],
  "decision": "ask_clarifier",
  "clarifying_question": "When you say propaganda, do you mean persuasive political advocacy, coordinated deceptive messaging, or something else?",
  "answer_constraints": [
    "avoid loaded framing",
    "define terms before conclusion"
  ]
}
```

This is a small addition, but it matters.
It turns ICA from a conceptual recommendation into a concrete orchestration contract.

---

## Why this is also a software architecture issue

This repo treats "agents" as software systems, not mystical entities.

An agent loop is usually ordinary program logic:

```python
while not done:
    state = read_state()
    step = policy(state)          # deterministic control logic where possible
    result = call_model_or_tool(step)
    update_state(result)
```

In a well-designed system, orchestration should be deterministic where possible.
Real agent systems still contain nondeterministic dependencies, including:

- model sampling
- retrieval ranking
- external API state
- timeouts
- race conditions

So the strong claim is not that every real system is fully deterministic.
It is that uncertainty should be isolated to model and external-system calls while the control logic remains explicit, inspectable, and testable.

ICA is therefore a deterministic orchestration improvement around probabilistic model calls.

---

## Illustrative token and latency impact

The following numbers are **illustrative rather than benchmarked**.
They show why selective clarification can reduce total cost.

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

At scale, that difference matters financially and operationally.

In ambiguous cases, **better questions can beat bigger answers**.

---

## Hidden baseline cost: correction funnels and silent failure

A low-token first answer is not necessarily an efficient answer.

In ambiguous prompts, the baseline model often chooses one interpretation implicitly and answers under that interpretation.
If the user meant something else, the conversation can enter a **correction funnel**:

1. the model answers the wrong version of the question
2. the user challenges the answer
3. the model defends or qualifies its interpretation
4. only later does the real issue become explicit: a load-bearing term was never defined

This is not just a retry problem.
It is a **wrong-funnel problem**.

Example pattern:

1. user asks: "Does Elon Musk post right-wing propaganda?"
2. model answers under one narrow definition of "propaganda"
3. user argues from a different definition
4. several turns later, the system finally reveals the real issue: the term "propaganda" was carrying multiple meanings

ICA moves that discovery to the front.
It exposes the load-bearing ambiguity before the system commits to an answer.

This matters because many users will not litigate the answer into correctness.
There are two baseline failure modes:

1. **Correction funnel**
The user pushes back, burns time and tokens, and eventually forces the model to discover the ambiguity.

2. **Silent failure**
The user does not push back, accepts or abandons the answer, and never learns that the answer depended on an undefined term.

So ICA should not be evaluated only on first-pass output tokens.
It should be evaluated on **tokens per resolved intent**:

`total cost = first answer + repair turns + user correction burden + silent-failure risk`

A short wrong answer is not cheaper than a short clarifying question if the answer sends the user down the wrong semantic funnel.

---

## Evaluation package

The biggest remaining credibility jump is empirical support.
This repo now includes a lightweight benchmark scaffold:

- prompt set: [`examples/ambiguous_prompts.csv`](examples/ambiguous_prompts.csv)
- protocol: [`eval/README.md`](eval/README.md)
- reporting template: [`eval/sample_results.md`](eval/sample_results.md)
- first-pass pilot benchmark: [`eval/pilot_results.md`](eval/pilot_results.md)
- machine-readable pilot table: [`eval/pilot_results.csv`](eval/pilot_results.csv)

The intended benchmark compares a direct-answer baseline against an ICA policy across 20 to 50 ambiguous prompts.

In practice, the more meaningful comparison is:

1. **Direct one-shot**
   - answer immediately and stop the measurement after the first assistant response
2. **Direct with repair funnel**
   - answer immediately, then include the cost of the user's correction and the eventual repair path
3. **ICA clarify-first**
   - ask the highest-value clarifier before the main answer when expected utility is positive

For ambiguous prompts, the second and third comparisons are the ones that matter most.
The first can make a wrong answer look artificially cheap simply because the measurement stops before the intent is actually resolved.

Primary outcome metrics:

- first assistant-message tokens
- total tokens per resolved task
- tokens per resolved intent
- clarification rate
- clarification hit rate
- retry count / loop depth
- latency to correct answer
- user-rated correctness
- user-rated clarity
- safety or premise-handling quality
- net utility versus an always-answer baseline
- definition-discovery turn
- correction-funnel depth
- user correction burden

Counter-metrics:

- over-clarification rate
- unnecessary clarification rate
- user abandonment after clarification
- false direct-answer rate
- false refusal / over-safety rate
- clarification bias score
- percentage of clarifiers that changed the final answer
- false-confidence rate
- silent-failure proxy
- percentage of ambiguous answers where the user never learns what term caused the mismatch

Those counter-metrics matter because ICA can fail in both directions:

- it can ask too often and annoy users
- it can ask too rarely and let ambiguity damage the answer

---

## Training and data recommendations

The clarification component should be trained on clarification-specific traces, not treated as a static prompt trick.

Useful training data includes:

- ambiguous real-world queries
- high-quality human clarifying questions
- accepted user intent resolutions
- adversarial prompt variants
- post-incident correction logs
- examples of false binaries and impossible premises
- prompts mixing real people, tragedy references, and requests for abuse

Useful model outputs at the control-layer stage include:

- ambiguity score
- risk score
- risk type labels
- intent hypotheses with probabilities
- candidate clarifiers with expected utilities
- recommended answer constraints

This is not just classic RLHF on final answers.
ICA creates a second, unusually valuable training signal:

- the user query was ambiguous
- the system proposed an interpretation split
- the user selected, corrected, ignored, or refined that split
- the final outcome shows whether the clarification was actually useful

That enables a layered training stack:

1. **Supervised training**
Train on ambiguous prompts and strong clarifying questions.

2. **Preference training / RLHF**
Prefer clarifiers that raters and users judge as neutral, short, informative, and non-leading.

3. **Outcome-based reward modeling**
Reward clarifiers that reduce retries, correction funnels, user abandonment, and unsafe outputs.

4. **Online experimentation**
Test thresholds, option counts, and clarifier styles on small traffic slices.

5. **Distillation**
Fold successful clarification behavior into smaller routing models and future base models.

That is what turns ICA into a self-improving control layer rather than a one-off workflow trick.

---

## Strategic implication: the clarification data flywheel

At large scale, ICA is not only a reliability pattern.
It becomes a **data flywheel**.

Every clarification interaction can produce a structured trace:

`ambiguous query -> candidate intents -> clarifying question -> user reply -> resolved intent -> final outcome`

That trace is more valuable than an ordinary chat log because it captures the missing hidden variable in many failed AI interactions:

> **what the user actually meant**

This matters strategically because the architecture itself is copyable.
The harder-to-copy advantage is the volume and diversity of real-world intent-resolution data.

OpenAI has publicly said ChatGPT has **more than 900 million weekly active users** and **more than 50 million consumer subscribers** in its 2026 post [Scaling AI for everyone](https://openai.com/index/scaling-ai-for-everyone/).
OpenAI has also published a privacy-preserving usage study based on **1.5 million conversations** in the context of **700 million weekly active users** in [How people are using ChatGPT](https://openai.com/index/how-people-are-using-chatgpt/).

OpenAI also says:

- consumer ChatGPT conversations can help improve models unless the user opts out in data controls, as described in [How ChatGPT learns about the world while protecting privacy](https://openai.com/index/how-chatgpt-protects-privacy/) and the Help Center article [What if I want to keep my history on but disable model training?](https://help.openai.com/en/articles/8983130-what-if-i-want-to-keep-my-history-on-but-disable-model-training%23.class)
- business and API inputs and outputs are **not used for training by default**, as described in [Business data privacy, security, and compliance](https://openai.com/business-data/)

So the strongest competitive argument is not:

- "ask more clarifying questions"

It is:

- market share can be converted into structured intent labels
- structured intent labels can train better ask-vs-answer policies
- better policies improve answer quality, safety, and trust
- improved trust and usefulness drive more usage
- more usage generates more clarification data

That is a clarification data flywheel.

The copyable layer includes:

- the architecture diagram
- the prompt pattern
- the idea of ambiguity scoring
- the UX flow

The harder-to-copy layer includes:

- real ambiguity distributions across domains and cultures
- user-selected intent labels
- live correction-funnel traces
- neutral clarifier outcome data
- calibrated thresholds for when not to ask
- multilingual edge cases and adversarial prompt patterns

So the defensible moat claim is:

> Competitors can copy the visible behavior of asking clarifying questions, but without comparable live usage volume they may struggle to match the trained clarification policy, ambiguity coverage, and intent-resolution feedback loop.

In that sense, ICA could turn market share into model-quality advantage.
Not just by having more conversations, but by converting ambiguous conversations into structured training data.

---

## Safety and refusal behavior

ICA is not only an efficiency pattern.
It is also a safety and truthfulness layer against adversarial or manipulative prompt framing.

However, the safe behavior is not always "ask a clarifying question."

For example, when a prompt is low ambiguity but clearly high risk, the right response may be:

- a direct refusal
- a safe redirect
- a premise-check that strips out a false causal framing

Safer example:

> "I can't help with abusive or exploitative content about real tragedies. If you'd like, I can help with a factual summary, a fictional satire with no real victims, or a discussion of why the framing is harmful."

This is better than asking the user to reconfirm harmful intent when the safe response would not change.

---

## Repository status

The README, architecture diagram, proposal DOCX, and proposal PDF in this repository are intended to describe the **same architecture revision**.
If one artifact is updated, the others should be regenerated to keep the package aligned.

---

## Final takeaway

ICA is not a mystical theory of intelligence.
It is a practical control-layer pattern for LLM systems:

- model ambiguity as uncertainty over intent
- compress that uncertainty before generation when clarification is worth the cost
- isolate uncertainty to model and external-system calls while keeping orchestration explicit
- choose the highest-utility clarifier rather than asking by default
- measure cost at the level of resolved intent, not just the first assistant response
- prevent wrong-funnel conversations and silent failures, not just visible retries
- treat ambiguity and risk as separate but jointly relevant signals
- refuse or redirect directly when clarification would not improve the safe response
- use clarification traces to improve the control layer over time

If we do that well, we get systems that are more precise, more reliable, more defensible, and often cheaper to run.
