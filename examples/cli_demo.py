"""Offline ICA demo using the mock provider.

Run from the repository root:

    python examples/cli_demo.py

The same engine can later be given a real provider adapter that implements
``generate_structured``. Tests and this demo do not require live API access.
"""

from __future__ import annotations

from ica_core import IntentCompressor, MockIntentProvider, PolicyConfig


def main() -> None:
    compressor = IntentCompressor(
        provider=MockIntentProvider(),
        policy_config=PolicyConfig(tau=0.15),
    )
    decision = compressor.process(
        "Does Elon Musk post right-wing propaganda?",
        trace_id="demo-001",
        metadata={"example": "cli_demo", "provider": "mock"},
    )

    print("ICA demo")
    print(f"decision: {decision.decision}")
    print(f"ambiguity_score: {decision.ambiguity_score:.2f}")
    print(f"risk_score: {decision.risk_score:.2f}")
    print(f"expected_utility: {decision.expected_utility:.2f}")
    print(f"selected_clarifier: {decision.clarifying_question}")
    print(f"rationale: {decision.rationale}")

    print("\nLater real-provider shape:")
    print("compressor = IntentCompressor(provider=YourProviderAdapter(...))")


if __name__ == "__main__":
    main()
