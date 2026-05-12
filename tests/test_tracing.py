import json

from ica_core.tracing import JSONLTraceSink, query_hash, redact_query


def test_jsonl_trace_sink_hashes_query_by_default(tmp_path) -> None:
    trace_path = tmp_path / "ica.jsonl"
    sink = JSONLTraceSink(trace_path)

    sink.record(
        "ica.process.start",
        {
            "trace_id": "trace-1",
            "query": "Email jane@example.com about account 123456.",
            "request_metadata": {"sensitive": "do-not-store"},
        },
    )

    row = json.loads(trace_path.read_text(encoding="utf-8").strip())

    assert row["name"] == "ica.process.start"
    assert row["query_hash"] == query_hash("Email jane@example.com about account 123456.")
    assert "query" not in row
    assert "request_metadata" not in row


def test_jsonl_trace_sink_can_store_redacted_query(tmp_path) -> None:
    trace_path = tmp_path / "ica.jsonl"
    sink = JSONLTraceSink(trace_path, query_mode="redacted")

    sink.record(
        "ica.process.start",
        {"query": "Email jane@example.com about account 123456."},
    )

    row = json.loads(trace_path.read_text(encoding="utf-8").strip())

    assert row["query_hash"]
    assert row["query_redacted"] == "Email [email] about account [number]."


def test_redact_query_truncates_long_text() -> None:
    redacted = redact_query("x" * 120, max_length=20)

    assert redacted == "xxxxxxxxxxxxxxxxx..."
