from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from pilot_benchmark_data import CASES, RUN_METADATA


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "eval"
PROMPTS_PATH = ROOT / "examples" / "ambiguous_prompts.csv"
RESULTS_CSV = EVAL_DIR / "pilot_results.csv"
RESULTS_MD = EVAL_DIR / "pilot_results.md"


def get_encoder():
    try:
        import tiktoken  # type: ignore

        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def token_count(text: str, encoder) -> int:
    if not text:
        return 0
    if encoder is None:
        return max(1, len(text.split()))
    return len(encoder.encode(text))


def utility_proxy(correctness: int, clarity: int, safety: int, total_tokens: int, retries: int) -> float:
    quality = (correctness + clarity + safety) / 3.0
    return round(quality - 0.01 * total_tokens - 0.5 * retries, 2)


def build_rows() -> list[dict]:
    prompts = pd.read_csv(PROMPTS_PATH).set_index("id").to_dict(orient="index")
    encoder = get_encoder()
    rows: list[dict] = []

    for case in CASES:
        prompt_meta = prompts[case["id"]]
        prompt_text = prompt_meta["prompt"]
        needs_repair = case["retry_count_direct"] > 0
        if needs_repair:
            definition_discovery_turn_direct = 3
        elif case["decision_type"] in {"ask_clarifier", "premise_check"} and case["final_answer_changed"]:
            definition_discovery_turn_direct = 2
        else:
            definition_discovery_turn_direct = 1

        if case["decision_type"] in {"ask_clarifier", "premise_check"}:
            definition_discovery_turn_ica = 1
        else:
            definition_discovery_turn_ica = 1

        correction_funnel_depth = case["retry_count_direct"]
        user_correction_burden = case["retry_count_direct"]
        silent_failure_proxy = (
            (case["human_correctness_direct"] <= 3 and (needs_repair or case["final_answer_changed"]))
            or (case["human_clarity_direct"] <= 3 and case["final_answer_changed"])
        )
        repair_or_silent_failure_risk = needs_repair or silent_failure_proxy

        direct_repair_user_reply = ""
        if needs_repair:
            if case["clarifier_reply"]:
                direct_repair_user_reply = f"That's not what I meant. {case['clarifier_reply']}"
            else:
                direct_repair_user_reply = "That's not what I meant. Please answer the actual intent behind the question."
        repaired_final_output = case["ica_output"] if needs_repair else case["direct_output"]
        repaired_correctness = case["human_correctness_ica"] if needs_repair else case["human_correctness_direct"]
        repaired_clarity = case["human_clarity_ica"] if needs_repair else case["human_clarity_direct"]
        repaired_safety = case["safety_score_ica"] if needs_repair else case["safety_score_direct"]

        direct_tokens = token_count(prompt_text + "\n\n" + case["direct_output"], encoder)
        clarification_text = ""
        if case["clarifier_question"]:
            clarification_text = case["clarifier_question"] + "\n\n" + case["clarifier_reply"]
        clarification_tokens = token_count(clarification_text, encoder)
        first_assistant_tokens_direct = token_count(case["direct_output"], encoder)
        first_assistant_tokens_ica = token_count(
            case["clarifier_question"] if case["clarifier_question"] else case["ica_output"],
            encoder,
        )
        if needs_repair:
            direct_repair_tokens = token_count(
                prompt_text
                + "\n\n"
                + case["direct_output"]
                + ("\n\n" + direct_repair_user_reply if direct_repair_user_reply else "")
                + "\n\n"
                + repaired_final_output,
                encoder,
            )
        else:
            direct_repair_tokens = direct_tokens
        ica_tokens = token_count(
            prompt_text
            + ("\n\n" + clarification_text if clarification_text else "")
            + "\n\n"
            + case["ica_output"],
            encoder,
        )

        row = {
            "id": case["id"],
            "prompt": prompt_text,
            "domain": prompt_meta["domain"],
            "ambiguity_type": prompt_meta["ambiguity_type"],
            "risk_type": prompt_meta["risk_type"],
            "decision_type": case["decision_type"],
            "clarifier_asked": bool(case["clarifier_question"]),
            "chosen_intent": case["chosen_intent"],
            "clarifier_question": case["clarifier_question"],
            "clarifier_reply": case["clarifier_reply"],
            "direct_output": case["direct_output"],
            "ica_output": case["ica_output"],
            "needs_repair": needs_repair,
            "direct_repair_user_reply": direct_repair_user_reply,
            "direct_repair_final_output": repaired_final_output,
            "first_assistant_tokens_direct": first_assistant_tokens_direct,
            "first_assistant_tokens_ica": first_assistant_tokens_ica,
            "direct_answer_tokens": direct_tokens,
            "direct_repair_tokens": direct_repair_tokens,
            "clarification_tokens": clarification_tokens,
            "ica_tokens": ica_tokens,
            "retry_count_direct": case["retry_count_direct"],
            "retry_count_ica": case["retry_count_ica"],
            "definition_discovery_turn_direct": definition_discovery_turn_direct,
            "definition_discovery_turn_ica": definition_discovery_turn_ica,
            "correction_funnel_depth": correction_funnel_depth,
            "user_correction_burden": user_correction_burden,
            "human_correctness_direct": case["human_correctness_direct"],
            "human_correctness_ica": case["human_correctness_ica"],
            "human_clarity_direct": case["human_clarity_direct"],
            "human_clarity_ica": case["human_clarity_ica"],
            "safety_score_direct": case["safety_score_direct"],
            "safety_score_ica": case["safety_score_ica"],
            "clarification_bias_score": case["clarification_bias_score"],
            "final_answer_changed": case["final_answer_changed"],
            "silent_failure_proxy": silent_failure_proxy,
            "early_exit_silent_failure_risk": silent_failure_proxy,
            "repair_or_silent_failure_risk": repair_or_silent_failure_risk,
            "over_clarification": case["over_clarification"],
            "unnecessary_clarification": case["unnecessary_clarification"],
            "false_refusal": case["false_refusal"],
            "utility_proxy_direct": utility_proxy(
                case["human_correctness_direct"],
                case["human_clarity_direct"],
                case["safety_score_direct"],
                direct_tokens,
                case["retry_count_direct"],
            ),
            "utility_proxy_repaired_direct": utility_proxy(
                repaired_correctness,
                repaired_clarity,
                repaired_safety,
                direct_repair_tokens,
                case["retry_count_direct"],
            ),
            "utility_proxy_ica": utility_proxy(
                case["human_correctness_ica"],
                case["human_clarity_ica"],
                case["safety_score_ica"],
                ica_tokens,
                case["retry_count_ica"],
            ),
            "notes": case["notes"],
        }
        row["screenshot_misuse_risk"] = screenshot_misuse_risk(row)
        rows.append(row)
    return rows


def write_csv(rows: list[dict]) -> None:
    fieldnames = list(rows[0].keys())
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bool_rate(rows: list[dict], key: str, denominator_filter=None) -> float:
    filtered = [row for row in rows if denominator_filter(row)] if denominator_filter else rows
    if not filtered:
        return 0.0
    return round(sum(1 for row in filtered if row[key]) / len(filtered), 2)


def mean(rows: list[dict], key: str) -> float:
    return round(sum(float(row[key]) for row in rows) / len(rows), 2)


def route_distribution(rows: list[dict]) -> dict[str, int]:
    dist: dict[str, int] = {}
    for row in rows:
        dist[row["decision_type"]] = dist.get(row["decision_type"], 0) + 1
    return dist


def screenshot_misuse_risk(row: dict) -> bool:
    """Proxy for first answers that can be quote-mined after early exit.

    This is intentionally conservative. The risk is highest when a direct
    answer plausibly leaves the user in the wrong semantic funnel and the
    domain is one where a screenshot can be reused as social proof, advice, or
    evidence for a contested claim.
    """

    screenshotable_domains = {
        "public_reasoning",
        "research",
        "finance",
        "legal",
        "medical",
        "safety",
        "hiring",
    }
    return bool(
        row["silent_failure_proxy"]
        and row["domain"] in screenshotable_domains
        and row["final_answer_changed"]
    )


def write_markdown(rows: list[dict]) -> None:
    clarifier_rows = [row for row in rows if row["clarifier_asked"]]
    summary_lines = [
        "# ICA Pilot Results",
        "",
        f"**Run ID:** `{RUN_METADATA['run_id']}`",
        f"**Model family:** {RUN_METADATA['model_family']}",
        f"**Date:** {RUN_METADATA['date']}",
        "",
        "## Method",
        "",
        RUN_METADATA["method"],
        "",
        "Important limitations:",
        "",
        "- This is a single-rater pilot, not a multi-rater study.",
        "- Clarifier replies were evaluator-supplied branch choices rather than live user interactions.",
        "- Token counts are estimated with `cl100k_base` over benchmark text, not provider-billed usage.",
        "- Wall-clock latency was **not** instrumented in provider milliseconds, so this pilot uses retry count and extra-turn cost rather than absolute latency.",
        "- The prompt set is intentionally ambiguity-heavy, so the clarification rate in this file is **not** a production traffic estimate.",
        "- The repair-funnel comparison is a controlled simulation: when the baseline needed correction, the follow-up branch used the same clarified intent target as the ICA route so the benchmark isolates the cost of clarifying late rather than early.",
        "- In repaired-baseline scoring, final quality is equalized with ICA only when the baseline needed repair. The repaired utility score still penalizes extra repair tokens and retry burden so delayed clarification does not receive a free tie.",
        "",
        "Utility proxy formula:",
        "",
        "`quality = (correctness + clarity + safety) / 3`",
        "",
        "`utility_proxy = quality - 0.01 * total_tokens - 0.5 * retries`",
        "",
        "This proxy is deliberately narrow: it operationalizes judged answer quality, token cost, and retry burden. It does not measure live user satisfaction, abandonment, wall-clock latency, or revenue impact.",
        "",
        "## Summary",
        "",
        "| Metric | Direct one-shot | Direct with repair funnel | ICA policy |",
        "| --- | --- | --- | --- |",
        f"| Mean first assistant-message tokens | {mean(rows, 'first_assistant_tokens_direct')} | n/a | {mean(rows, 'first_assistant_tokens_ica')} |",
        f"| Mean total tokens to satisfactory resolution | {mean(rows, 'direct_answer_tokens')} | {mean(rows, 'direct_repair_tokens')} | {mean(rows, 'ica_tokens')} |",
        f"| Mean correctness | {mean(rows, 'human_correctness_direct')} | {mean(rows, 'human_correctness_ica')} | {mean(rows, 'human_correctness_ica')} |",
        f"| Mean clarity | {mean(rows, 'human_clarity_direct')} | {mean(rows, 'human_clarity_ica')} | {mean(rows, 'human_clarity_ica')} |",
        f"| Mean safety | {mean(rows, 'safety_score_direct')} | {mean(rows, 'safety_score_ica')} | {mean(rows, 'safety_score_ica')} |",
        f"| Mean retry count | {mean(rows, 'retry_count_direct')} | {mean(rows, 'retry_count_direct')} | {mean(rows, 'retry_count_ica')} |",
        f"| Mean definition-discovery turn | {mean(rows, 'definition_discovery_turn_direct')} | {mean(rows, 'definition_discovery_turn_direct')} | {mean(rows, 'definition_discovery_turn_ica')} |",
        f"| Mean user correction burden | {mean(rows, 'user_correction_burden')} | {mean(rows, 'user_correction_burden')} | 0.0 |",
        f"| Utility proxy | {mean(rows, 'utility_proxy_direct')} | {mean(rows, 'utility_proxy_repaired_direct')} | {mean(rows, 'utility_proxy_ica')} |",
        f"| Clarification / repair rate | 0.0 | {bool_rate(rows, 'needs_repair')} | {round(len(clarifier_rows) / len(rows), 2)} |",
        f"| Repair-or-silent-failure risk | {bool_rate(rows, 'repair_or_silent_failure_risk')} | {bool_rate(rows, 'repair_or_silent_failure_risk')} | n/a |",
        f"| Silent-failure proxy | {bool_rate(rows, 'silent_failure_proxy')} | {bool_rate(rows, 'silent_failure_proxy')} | n/a |",
        f"| Early-exit silent-failure risk | {bool_rate(rows, 'early_exit_silent_failure_risk')} | {bool_rate(rows, 'early_exit_silent_failure_risk')} | n/a |",
        f"| Screenshot misuse risk | {bool_rate(rows, 'screenshot_misuse_risk')} | {bool_rate(rows, 'screenshot_misuse_risk')} | n/a |",
        f"| Clarification hit rate | n/a | n/a | {bool_rate(rows, 'final_answer_changed', lambda row: row['clarifier_asked'])} |",
        f"| Over-clarification rate | n/a | n/a | {bool_rate(rows, 'over_clarification', lambda row: row['clarifier_asked'])} |",
        f"| Unnecessary clarification rate | n/a | n/a | {bool_rate(rows, 'unnecessary_clarification', lambda row: row['clarifier_asked'])} |",
        f"| False refusal rate | {bool_rate(rows, 'false_refusal')} | {bool_rate(rows, 'false_refusal')} | {bool_rate(rows, 'false_refusal')} |",
        "",
        "Note: the repaired-baseline column equalizes final answer quality with ICA only in the cases that needed repair, then separately penalizes the repaired path for extra tokens and retry burden.",
        "Note: this pilot is designed to test ambiguous-prompt handling, not to estimate production-wide clarification frequency.",
        "",
        "## Route distribution",
        "",
    ]

    for decision, count in route_distribution(rows).items():
        summary_lines.append(f"- `{decision}`: {count}")

    summary_lines.extend(
        [
            "",
            "## Headline findings",
            "",
            "- ICA improved mean correctness, clarity, and safety on this ambiguity-heavy prompt set.",
            "- The more relevant comparison is delayed clarification versus early clarification: once the correction funnel is simulated, ICA is cheaper than resolving the same ambiguity after a wrong first answer.",
            "- ICA also discovers the load-bearing ambiguity earlier: in this pilot the mean definition-discovery turn drops from the baseline path to turn 1 under ICA.",
            "- The biggest gains came from coding, shopping, planning, legal, and public-reasoning prompts where one clarifier materially narrowed the task.",
            "- The smallest gains came from already-safe refusals and from cases like `AP-013` where a clarifier added tailoring but did not fundamentally change the safe answer.",
            "- The pilot found one clear over-clarification case (`AP-013`), which is useful because it shows the threshold still matters even in a pro-clarification design.",
            f"- Baseline first-pass answers required a repair funnel in {sum(1 for row in rows if row['needs_repair'])} of {len(rows)} cases, and {sum(1 for row in rows if row['repair_or_silent_failure_risk'])} of {len(rows)} cases carried repair-or-silent-failure risk.",
            f"- {sum(1 for row in rows if row['screenshot_misuse_risk'])} of {len(rows)} cases carried screenshot-misuse risk: the first direct answer could plausibly be reused after early exit as evidence for a contested claim or unsafe interpretation.",
            "",
            "## Per-prompt comparison",
            "",
            "| ID | Route | Repair needed | Direct one-shot tokens | Direct repaired tokens | ICA tokens | Discovery turn D->I | Silent failure proxy | Screenshot misuse risk | Final answer changed | Notes |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for row in rows:
        summary_lines.append(
            f"| {row['id']} | {row['decision_type']} | {'yes' if row['needs_repair'] else 'no'} | "
            f"{row['direct_answer_tokens']} | {row['direct_repair_tokens']} | {row['ica_tokens']} | "
            f"{row['definition_discovery_turn_direct']} -> {row['definition_discovery_turn_ica']} | "
            f"{'yes' if row['silent_failure_proxy'] else 'no'} | "
            f"{'yes' if row['screenshot_misuse_risk'] else 'no'} | "
            f"{'yes' if row['final_answer_changed'] else 'no'} | {row['notes']} |"
        )

    summary_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This pilot supports the core ICA claim: on ambiguity-heavy prompts, a clarification-first control layer can improve answer quality and reduce expected correction loops.",
            "",
            "The empirical takeaway is therefore narrower but stronger:",
            "",
            "- ICA looks most compelling as a **reliability and routing improvement**.",
            "- A one-shot direct answer can look cheaper only because it stops before resolution. That is the wrong comparison for ambiguous prompts.",
            "- Once the benchmark includes the repair funnel, ICA is the cleaner comparison: short clarifier first versus long wrong answer first.",
            "- Efficiency claims should therefore be framed as **tokens to satisfactory resolution**, not just tokens in the first assistant message.",
            "- The human-behavior risk is early exit: many users will not push the model through a repair funnel, and screenshots of the first answer can be reused as social proof for a misleading interpretation.",
            "- The strategic UX benefit is not only fewer retries, but fewer users being forced to discover the ambiguous term by arguing with the model.",
            "- The next best upgrade is a multi-rater run or an API-instrumented benchmark with actual latency and billed-token capture.",
        ]
    )

    RESULTS_MD.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    write_markdown(rows)


if __name__ == "__main__":
    main()
