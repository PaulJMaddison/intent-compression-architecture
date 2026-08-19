"""Privacy-conscious tracing utilities for ICA orchestration."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Protocol

from ica_core.schemas import ClarifierOutput

QueryTraceMode = Literal["hash", "redacted", "raw", "none"]


@dataclass(frozen=True)
class TraceEvent:
    """One structured trace event emitted by the engine."""

    name: str
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable event representation."""

        return {"timestamp": self.timestamp.isoformat(), "name": self.name, **self.payload}


class TraceSink(Protocol):
    """Destination for controller trace events."""

    def record(self, name: str, payload: dict[str, Any]) -> None:
        """Record a trace event."""


class NoOpTraceSink:
    """Trace sink that intentionally drops events."""

    def record(self, name: str, payload: dict[str, Any]) -> None:
        del name, payload


class InMemoryTraceSink:
    """Trace sink useful for tests, demos, and local instrumentation."""

    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def record(self, name: str, payload: dict[str, Any]) -> None:
        self.events.append(TraceEvent(name=name, payload=dict(payload)))


class JSONLTraceSink:
    """Append lightweight intent-resolution traces to a local JSONL file.

    Raw query text, clarifier text, and request metadata are excluded by default.
    Query text can be hashed, coarsely redacted, stored raw, or omitted. Clarifier
    text is hashed unless ``include_clarifier_text=True`` is explicitly selected.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        query_mode: QueryTraceMode = "hash",
        include_request_metadata: bool = False,
        include_clarifier_text: bool = False,
    ) -> None:
        self.path = Path(path)
        self.query_mode = query_mode
        self.include_request_metadata = include_request_metadata
        self.include_clarifier_text = include_clarifier_text

    def record(self, name: str, payload: dict[str, Any]) -> None:
        event = TraceEvent(name=name, payload=self._sanitize_payload(payload))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(event.to_json_dict(), sort_keys=True) + "\n"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(serialized)

    def _sanitize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        sanitized = dict(payload)

        query = sanitized.pop("query", None)
        if isinstance(query, str):
            sanitized.update(query_trace_fields(query, mode=self.query_mode))

        clarifying_question = sanitized.pop("clarifying_question", None)
        if isinstance(clarifying_question, str):
            if self.include_clarifier_text:
                sanitized["clarifying_question"] = clarifying_question
            else:
                sanitized["clarifying_question_hash"] = text_hash(clarifying_question)

        if not self.include_request_metadata:
            sanitized.pop("request_metadata", None)
            metadata = sanitized.get("metadata")
            if isinstance(metadata, dict):
                sanitized["metadata"] = {
                    key: value for key, value in metadata.items() if key != "request_metadata"
                }

        return _json_safe(sanitized)


def text_hash(text: str) -> str:
    """Return a short stable hash for privacy-preserving trace joins."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def query_hash(query: str) -> str:
    """Backward-compatible alias for hashing query text."""

    return text_hash(query)


def redact_query(query: str, *, max_length: int = 96) -> str:
    """Return a coarse redacted query preview for local debugging.

    This is intentionally a convenience redactor, not a DLP or anonymisation
    system. Production systems should apply their own data-classification and
    retention controls before persisting user content.
    """

    redacted = re.sub(r"[\w.+-]+@[\w.-]+\.\w+", "[email]", query)
    redacted = re.sub(r"\b\d{3,}\b", "[number]", redacted)
    redacted = re.sub(r"\s+", " ", redacted).strip()
    if len(redacted) > max_length:
        return redacted[: max_length - 3].rstrip() + "..."
    return redacted


def query_trace_fields(query: str, *, mode: QueryTraceMode = "hash") -> dict[str, str]:
    """Build query trace fields according to the requested privacy mode."""

    if mode == "none":
        return {}
    if mode == "raw":
        return {"query": query}
    if mode == "redacted":
        return {"query_hash": query_hash(query), "query_redacted": redact_query(query)}
    return {"query_hash": query_hash(query)}


def decision_trace_payload(decision: ClarifierOutput) -> dict[str, Any]:
    """Extract high-value routing fields for the clarification data flywheel."""

    metadata = decision.metadata or {}
    return {
        "trace_id": decision.trace_id,
        "decision": decision.decision,
        "ambiguity_score": decision.ambiguity_score,
        "risk_score": decision.risk_score,
        "intent_entropy_bits": decision.intent_entropy_bits,
        "selected_clarifier_id": decision.selected_clarifier_id,
        "clarifying_question": decision.clarifying_question,
        "expected_utility": decision.expected_utility,
        "estimated_token_savings": decision.estimated_token_savings,
        "source": metadata.get("source"),
        "fallback": bool(metadata.get("fallback")),
        "provider_name": metadata.get("provider_name"),
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
