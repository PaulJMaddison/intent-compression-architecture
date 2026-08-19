# KynticAI Clarity Gateway — Reference Archive

> **Status: historical/reference archive.** This repository preserves the engineering lineage that led from **Intent Compression Architecture (ICA)** to the KynticAI **Clarity Gateway**. It is intentionally useful, executable, and reproducible, but it is **not the active product source of truth**.

ICA started from a simple failure mode: an AI system can give a plausible answer before it has resolved what the user actually means. The work in this archive turned that observation into a control-plane design: model-assisted intent hypotheses, separate ambiguity and risk signals, deterministic routing, an expected-utility gate for clarification, structured outputs, traceable decisions, and later an agentic task-state framing.

This archive exists so that evolution remains inspectable rather than being overwritten by the current implementation.

## Start here

- **How the idea evolved:** [`EVOLUTION.md`](EVOLUTION.md)
- **Archive preservation rules:** [`ARCHIVE_POLICY.md`](ARCHIVE_POLICY.md)
- **Original long-form README snapshot:** [`docs/legacy/README-2026-08-18.md`](docs/legacy/README-2026-08-18.md)
- **Original website snapshot:** [`docs/legacy/index-2026-08-18.html`](docs/legacy/index-2026-08-18.html)
- **Engineering proposal:** [`ICA_Engineering_Design_Proposal1.pdf`](ICA_Engineering_Design_Proposal1.pdf)
- **Architecture diagram:** [`diagrams/architecture.png`](diagrams/architecture.png)
- **Machine-readable decision contract:** [`spec/clarifier_output.schema.json`](spec/clarifier_output.schema.json)
- **Reference Python package:** [`src/ica_core/`](src/ica_core/)
- **Evaluation material:** [`eval/`](eval/)
- **Applied UCL example:** [`examples/ucl_relationship_intelligence.md`](examples/ucl_relationship_intelligence.md)

## What this archive established

The historical implementation makes several architectural ideas concrete:

1. **Intent is a control-plane concern.** Ambiguity is handled before answer generation or agent action rather than repaired only after a wrong first move.
2. **Clarification should be selective.** The core rule is `ask iff max_q U(q | x) > tau`: clarification has to earn the extra turn.
3. **Ambiguity and risk are different signals.** A clear but risky request is not treated as merely ambiguous, and a false premise can route differently from an ordinary clarifier.
4. **Probabilistic estimates can feed deterministic orchestration.** The provider proposes structured estimates; local policy code selects the route.
5. **Control decisions should be inspectable.** The reference contract exposes hypotheses, scores, candidate clarifiers, selected route, constraints, and audit metadata.
6. **The same principle extends to agents.** The later work reframed intent compression as preserving verified task state while filtering semantic noise and avoiding repeated failed actions.

## What it does *not* establish

This repository should not be read as evidence that the archived Python package is the current Clarity Gateway, that its mock-provider probabilities are calibrated production estimates, or that the pilot benchmark generalises to production traffic. No live provider adapter is bundled here and no hosted gateway is represented by this code.

The evaluation material is preserved because it shows how the thesis was tested and refined. Its limitations are part of the archive, not something to hide.

## Evolution at a glance

| Period | Milestone | Why it mattered |
| --- | --- | --- |
| May 2026 | Ambiguous-prompt pilot and correction-funnel analysis | Moved the problem from “bad answers” to **wrong semantic funnels** and silent failure. |
| May 2026 | Reproducible local validation | Made the proposal testable without paid APIs; local validation deliberately became canonical. |
| May 2026 | `ica-core` v0.1.0 | Turned the idea into a provider boundary, typed contract, deterministic policy, CLI, tests, and privacy-aware tracing. |
| May 2026 | ICA v1.0.0 | Consolidated the expected-utility policy, canonical example, benchmark framing, and proposal artefacts. |
| May 2026 | Agentic control-plane framing | Extended the same principle from chat clarification to long-running task-state control. |
| June 2026 | UCL relationship-intelligence example | Showed that clarification matters when ambiguity changes retrieval scope, evidence pack, or action. |
| June–August 2026 | Archive transition | Preserved ICA as historical lineage while active Clarity Gateway implementation moved elsewhere. |
| August 2026 | Archive hardening | Added explicit provenance, contract-parity checks, stronger invariants, safer tracing, and a clean public archive front door. |

See [`EVOLUTION.md`](EVOLUTION.md) for commit-linked detail.

## Reference implementation

The Python package remains executable because an architecture archive is more valuable when its contracts and decisions can still be replayed.

### Core package and tests

```bash
python -m venv .venv
# activate the virtual environment for your shell
python -m pip install -e ".[dev]"
python -m pytest
```

### Full archive validation

The proposal/evaluation artefact tooling uses the additional dependencies in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
bash scripts/validate_local.sh
```

PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
.\scripts\validate_local.ps1
```

`requirements.lock` pins the **archive artefact/evaluation toolchain**. It is not a complete lock of the package plus all development dependencies.

The validation path checks Python compilation, JSON Schema validity, schema/Pydantic contract parity, tests, package build, CLI smoke paths, the example CLI, and pilot report generation. It remains local by design; an earlier GitHub Actions schema workflow was intentionally removed when local reproducibility became canonical.

## Contract integrity

The hand-authored JSON Schema is the portable contract and the Pydantic models are the executable reference model. `scripts/validate_contract_parity.py` prevents their top-level and nested field sets from silently drifting apart.

Additional runtime invariants include:

- non-blank intent labels and clarifier questions
- finite scores and non-negative information gain
- unique candidate clarifier IDs
- selected IDs that reference real candidates
- an `ask_clarifier` route that names the selected candidate

These checks harden the reference implementation without changing the historical routing thesis.

## Tracing and privacy

Tracing is off by default. When JSONL tracing is enabled, query text is hashed by default and clarifying-question text is now hashed as well. Raw query capture and raw clarifier capture require separate explicit opt-ins.

The built-in redactor is deliberately described as coarse debugging assistance, **not** a production DLP or anonymisation system. A real deployment still needs its own retention, consent, access-control, and data-classification policy.

## Maintenance model

Historical snapshots and published artefacts are preserved rather than silently modernised. Maintained archive surfaces — this README, the reference runtime, contract validation, security notes, and evolution map — can be improved as long as the changes do not rewrite what the historical milestones claimed at the time.

See [`ARCHIVE_POLICY.md`](ARCHIVE_POLICY.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

No live API credential is required for the normal test or demo path. Do not add real keys, tokens, customer data, or private prompts to fixtures, traces, issues, or committed `.env` files. See [`SECURITY.md`](SECURITY.md).

## License

MIT. See [`LICENSE`](LICENSE).

## Author

Paul Maddison — KynticAI.
