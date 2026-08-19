# KynticAI Clarity Gateway — Reference Archive

> **This is a historical reference repo.** It shows how the ideas behind KynticAI's Clarity Gateway developed. It is not the current production Clarity Gateway code.

## What is this?

This repo preserves an earlier project called **Intent Compression Architecture (ICA)**.

ICA started from a simple problem:

**AI systems often answer before they are sure what the user actually means.**

For example:

> "Make this API faster."

That could mean:

- reduce response time
- handle more users at once
- use less compute
- make development faster

If an AI guesses the wrong meaning, it can spend a lot of time producing a good answer to the wrong question.

ICA explored a better approach: **work out whether the meaning is clear before acting.**

If the meaning is clear, answer normally.

If one short question would prevent a much bigger mistake, ask that question first.

That basic idea later became part of the thinking behind the **KynticAI Clarity Gateway**.

## The main idea in plain English

The system looks at a request before the main AI answers or takes an action.

It asks four simple questions:

1. **Is the request clear?**
2. **Could it reasonably mean more than one thing?**
3. **Would choosing the wrong meaning materially change the answer or action?**
4. **Is asking one short question more useful than guessing?**

It then chooses one of four actions:

- **Answer directly** — the request is clear enough.
- **Ask a question** — one short clarification could prevent a wrong answer.
- **Check the premise** — the request may be based on something false or misleading.
- **Refuse or redirect** — the request should not be completed as written.

The important point is that the system does **not** ask questions all the time. It only asks when the extra question is likely to save more time, mistakes, risk or wasted work than it costs.

## Why this mattered

The original work moved through several stages.

First, it focused on ambiguous chat questions and the cost of answering the wrong interpretation.

Then it turned that idea into working Python code with:

- a clear decision format
- simple routing rules
- tests
- a command-line demo
- local tracing
- benchmark examples

Later, the same idea was applied to AI agents and coding tools.

For an agent, the problem is not only understanding the first question. It also needs to remember:

- the original goal
- what has already been proved
- what failed
- what constraints still matter
- what the next useful action is

That is the bridge from the original ICA work to the later **Clarity Gateway** direction.

## Where to look

If you want to understand the project without reading everything, start here:

- [`EVOLUTION.md`](EVOLUTION.md) — how the idea changed over time, linked to the original commits
- [`ICA_Engineering_Design_Proposal1.pdf`](ICA_Engineering_Design_Proposal1.pdf) — the original engineering proposal
- [`diagrams/architecture.png`](diagrams/architecture.png) — the architecture diagram
- [`src/ica_core/`](src/ica_core/) — the working Python reference code
- [`spec/clarifier_output.schema.json`](spec/clarifier_output.schema.json) — the decision format used by the reference implementation
- [`eval/`](eval/) — the early benchmark and evaluation work
- [`examples/ucl_relationship_intelligence.md`](examples/ucl_relationship_intelligence.md) — an example of applying the idea to retrieval and relationship data

The older long-form material has not been deleted. It is preserved exactly as historical material:

- [`docs/legacy/README-2026-08-18.md`](docs/legacy/README-2026-08-18.md)
- [`docs/legacy/index-2026-08-18.html`](docs/legacy/index-2026-08-18.html)

## Important limitation

The Python code in this repo is a **reference implementation**, not the current Clarity Gateway.

It uses an offline mock provider so the behaviour can be tested without paid APIs or real credentials.

The early benchmark results are also historical experiments. They show how the idea was tested and improved; they should not be treated as proof of current production performance.

## Running the reference code

Create a Python environment and install the package:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
```

For the full archive checks:

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
bash scripts/validate_local.sh
```

On Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
.\scripts\validate_local.ps1
```

## GitHub Actions

**GitHub Actions are intentionally not used in this repository.**

There are no workflow files under `.github/workflows`, so pushes and pull requests do not start GitHub Actions jobs from this repo.

Validation is deliberately run locally using the scripts above. This preserves the way the archive was designed and avoids adding cloud automation to a historical reference project.

## Privacy and security

Normal tests do not need real API keys.

Do not add:

- API keys or access tokens
- customer data
- private prompts
- production traces
- real `.env` files

Tracing is off by default. When enabled, query and clarification text are protected by safer defaults unless raw capture is explicitly requested.

See [`SECURITY.md`](SECURITY.md) for more detail.

## Preserving the history

This repo is useful because it shows **how the idea evolved**, including its early assumptions and limitations.

Historical files should therefore be preserved rather than silently rewritten to look like the current product.

See [`ARCHIVE_POLICY.md`](ARCHIVE_POLICY.md) for the preservation rules.

## License

MIT. See [`LICENSE`](LICENSE).

## Author

Paul Maddison — KynticAI.
