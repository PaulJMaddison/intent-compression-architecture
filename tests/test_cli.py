import json

import pytest

from ica_core.cli import main


def test_cli_readable_mock_output(capsys) -> None:
    exit_code = main(["Make this API faster."])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "decision: ask_clarifier" in captured.out
    assert "ambiguity_score:" in captured.out
    assert "selected_clarifier:" in captured.out


def test_cli_json_output(capsys) -> None:
    exit_code = main(["--json", "Explain transformers simply."])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["decision"] == "answer_direct"
    assert "ambiguity_score" in payload


def test_cli_trace_writes_jsonl_without_raw_query(tmp_path, capsys) -> None:
    trace_path = tmp_path / "trace.jsonl"

    exit_code = main(["--trace", "--trace-path", str(trace_path), "Make this API faster."])

    captured = capsys.readouterr()
    rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
    ]

    assert exit_code == 0
    assert f"trace_written: {trace_path}" in captured.out
    assert rows[0]["name"] == "ica.process.start"
    assert "query_hash" in rows[0]
    assert "query" not in rows[0]
    assert rows[-1]["name"] == "ica.process.decision"
    assert rows[-1]["decision"] == "ask_clarifier"


def test_cli_dry_run_does_not_require_provider(capsys) -> None:
    exit_code = main(["--dry-run", "--provider", "future", "Make this API faster."])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "dry_run: true" in captured.out
    assert "provider: future" in captured.out


def test_cli_rejects_unknown_live_provider() -> None:
    with pytest.raises(SystemExit):
        main(["--provider", "future", "Make this API faster."])
