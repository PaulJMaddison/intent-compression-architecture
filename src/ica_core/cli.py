"""Command line entrypoint for ICA core."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4

from ica_core.config import ICAConfig
from ica_core.core import CONTROL_SYSTEM_PROMPT, IntentCompressor
from ica_core.policy import PolicyConfig
from ica_core.providers.base import IntentProvider
from ica_core.providers.mock import MockIntentProvider
from ica_core.schemas import ClarifierOutput
from ica_core.tracing import JSONLTraceSink, NoOpTraceSink


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ica",
        description="Run the ICA clarification-first control layer.",
    )
    parser.add_argument("query", nargs="*", help="User query. Reads stdin when omitted.")
    parser.add_argument("--provider", default=None, help="Provider adapter name. Default: mock.")
    parser.add_argument("--model", default=None, help="Model name to pass through metadata.")
    parser.add_argument("--query-id", default=None, help="Optional compatibility trace/request id.")
    parser.add_argument("--trace-id", default=None, help="Explicit trace id. Generated when tracing.")
    parser.add_argument(
        "--threshold",
        "--tau",
        dest="tau",
        type=float,
        default=None,
        help="Expected-utility threshold for clarification.",
    )
    parser.add_argument("--verbose", action="store_true", help="Show extra routing context.")
    parser.add_argument("--json", action="store_true", help="Print the full decision as JSON.")
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Append privacy-conscious JSONL traces.",
    )
    parser.add_argument(
        "--trace-path",
        default="ica-traces.jsonl",
        help="Trace JSONL path used with --trace. Default: ica-traces.jsonl.",
    )
    parser.add_argument(
        "--trace-query",
        choices=("hash", "redacted", "raw", "none"),
        default="hash",
        help="How query text is represented in traces. Default: hash.",
    )
    parser.add_argument(
        "--trace-metadata",
        action="store_true",
        help="Include request metadata in traces. Off by default.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the planned provider call without running analysis.",
    )
    parser.add_argument(
        "--non-strict",
        action="store_true",
        help="Return explicit fallback decisions instead of raising provider/validation errors.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    query = _read_query(args.query)
    if not query:
        parser.error("a query is required via arguments or stdin")

    config = ICAConfig()
    provider_name = (args.provider or config.provider).lower()
    model_name = args.model or config.model_name
    tau = args.tau if args.tau is not None else config.tau
    trace_path = args.trace_path if args.trace else None
    trace_id = args.trace_id or args.query_id or (f"trace-{uuid4().hex}" if args.trace else None)

    if args.dry_run:
        _print_dry_run(
            query=query,
            provider_name=provider_name,
            model_name=model_name,
            tau=tau,
            trace_path=trace_path,
            trace_id=trace_id,
            json_output=args.json,
        )
        return 0

    try:
        provider = _build_provider(provider_name)
    except ValueError as exc:
        parser.error(str(exc))

    trace_sink = (
        JSONLTraceSink(
            Path(trace_path),
            query_mode=args.trace_query,
            include_request_metadata=args.trace_metadata,
        )
        if args.trace
        else NoOpTraceSink()
    )
    compressor = IntentCompressor(
        provider=provider,
        policy_config=PolicyConfig(tau=tau),
        strict=not args.non_strict,
        trace_sink=trace_sink,
    )
    decision = compressor.process(
        query,
        trace_id=trace_id,
        metadata={
            "cli_provider": provider_name,
            "model": model_name,
        },
    )

    if args.json:
        print(json.dumps(decision.model_dump(mode="json"), indent=2))
    else:
        _print_readable(decision, verbose=args.verbose, trace_path=trace_path)

    return 0


def _read_query(query_parts: list[str]) -> str:
    if query_parts:
        return " ".join(query_parts).strip()
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read().strip()


def _build_provider(provider_name: str) -> IntentProvider:
    if provider_name == "mock":
        return MockIntentProvider()
    raise ValueError(
        f"provider '{provider_name}' is not available in this build; use --provider mock"
    )


def _print_readable(
    decision: ClarifierOutput,
    *,
    verbose: bool,
    trace_path: str | None,
) -> None:
    print(f"decision: {decision.decision}")
    print(f"ambiguity_score: {decision.ambiguity_score:.2f}")
    print(f"risk_score: {decision.risk_score:.2f}")
    print(f"intent_entropy_bits: {decision.intent_entropy_bits:.2f}")
    if decision.expected_utility is not None:
        print(f"expected_utility: {decision.expected_utility:.2f}")
    if decision.estimated_token_savings is not None:
        print(f"estimated_token_savings: {decision.estimated_token_savings:.0f}")
    if decision.clarifying_question:
        print(f"selected_clarifier: {decision.clarifying_question}")
    if decision.safe_redirect:
        print(f"safe_redirect: {decision.safe_redirect}")
    print(f"rationale: {decision.rationale}")

    metadata = decision.metadata or {}
    if verbose:
        print(f"trace_id: {decision.trace_id}")
        print(f"source: {metadata.get('source')}")
        print(f"fallback: {metadata.get('fallback')}")
        print(f"provider: {metadata.get('provider_name')}")
        print(f"provider_proposed_decision: {metadata.get('provider_proposed_decision')}")
        if decision.answer_constraints:
            print("answer_constraints:")
            for constraint in decision.answer_constraints:
                print(f"  - {constraint}")

    if trace_path:
        print(f"trace_written: {trace_path}")


def _print_dry_run(
    *,
    query: str,
    provider_name: str,
    model_name: str,
    tau: float,
    trace_path: str | None,
    trace_id: str | None,
    json_output: bool,
) -> None:
    payload = {
        "dry_run": True,
        "provider": provider_name,
        "model": model_name,
        "tau": tau,
        "trace_id": trace_id,
        "trace_path": trace_path,
        "query_length": len(query),
        "system_instructions": CONTROL_SYSTEM_PROMPT,
        "response_model": "ClarifierOutput",
    }
    if json_output:
        print(json.dumps(payload, indent=2))
        return

    print("dry_run: true")
    print(f"provider: {provider_name}")
    print(f"model: {model_name}")
    print(f"tau: {tau}")
    print(f"trace_id: {trace_id}")
    print(f"trace_path: {trace_path}")
    print(f"query_length: {len(query)}")
    print("response_model: ClarifierOutput")


if __name__ == "__main__":
    raise SystemExit(main())
