"""S4 ablation: each question through the Auto Ontology arm and the
raw-schema arm, same chat model and generation settings, exact scoring.

An arm exposes ``model``, ``settings`` (dict with at least temperature and
max_tokens) and ``ask(question) -> {"value", "sql", "provenance"?}``.
"""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_SETTINGS = ("temperature", "max_tokens")


def _number(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().replace(",", ""))
        except ValueError:
            return None
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return _number(value[0])
    return None


def score_answer(value, expected, answer_type: str) -> bool:
    """Numbers equal after rounding to 2 decimals; sets equal ignoring
    order. Anything else, including no answer, is incorrect."""
    if answer_type == "number":
        got = _number(value)
        return got is not None and round(got, 2) == round(float(expected), 2)
    if answer_type == "set":
        if not isinstance(value, (list, tuple, set)) or not value:
            return False
        return {str(v).strip() for v in value} == {str(v).strip() for v in expected}
    raise ValueError(f"unknown answer_type {answer_type!r}")


def has_provenance(provenance) -> bool:
    return bool(provenance)


def raw_schema_prompt(question: str, schema: str) -> str:
    return (
        "You write one SQLite query that answers the question below. The data lives in "
        "two databases, attached as schema a (Source A) and schema b (Source B); qualify "
        "every table with its schema, for example a.table_name. Use only the schema below.\n\n"
        f"Schema:\n{schema}\n"
        f"Question: {question}\n\n"
        'Reply with JSON only: {"sql": "<one SQLite SELECT statement>"}'
    )


def _check_arms(ontology_arm, raw_arm) -> dict:
    if ontology_arm.model != raw_arm.model:
        raise ValueError(f"arms use different models: {ontology_arm.model!r} vs {raw_arm.model!r}")
    if dict(ontology_arm.settings) != dict(raw_arm.settings):
        raise ValueError("arms use different generation settings")
    missing = [k for k in REQUIRED_SETTINGS if k not in ontology_arm.settings]
    if missing:
        raise ValueError(f"generation settings lack {missing}")
    return {"model": ontology_arm.model, "settings": dict(ontology_arm.settings)}


def _ask(arm, question, record_provenance: bool) -> dict:
    try:
        answer = arm.ask(question) or {}
        row = {"value": answer.get("value"), "sql": answer.get("sql"), "error": answer.get("error")}
        if record_provenance:
            row["provenance_detail"] = answer.get("provenance")
            row["provenance"] = has_provenance(answer.get("provenance"))
        if answer.get("response") is not None:
            row["response"] = answer.get("response")
    except Exception as exc:  # an arm failure is recorded as no answer
        row = {"value": None, "sql": None, "error": f"{type(exc).__name__}: {exc}"}
        if record_provenance:
            row["provenance_detail"] = None
            row["provenance"] = False
    row["correct"] = score_answer(row["value"], question["expected"], question["answer_type"])
    return row


def run(questions, ontology_arm, raw_arm, out_dir) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    generation = _check_arms(ontology_arm, raw_arm)
    # Ground truth is fixed on disk before any model is asked.
    (out_dir / "ground_truth.json").write_text(json.dumps([
        {"id": q["id"], "answer_type": q["answer_type"], "expected": q["expected"],
         "reference_sql": q.get("reference_sql")}
        for q in questions
    ], indent=2))
    (out_dir / "generation_settings.json").write_text(json.dumps(generation, indent=2))
    rows = []
    for q in questions:
        rows.append({
            "id": q["id"],
            "question": q.get("question"),
            "answer_type": q["answer_type"],
            "conflict_ids": q.get("conflict_ids", []),
            "expected": q["expected"],
            "ontology": _ask(ontology_arm, q, record_provenance=True),
            "raw": _ask(raw_arm, q, record_provenance=False),
        })
    onto = sum(r["ontology"]["correct"] for r in rows)
    raw = sum(r["raw"]["correct"] for r in rows)
    summary = {"total": len(rows), "ontology_correct": onto, "raw_correct": raw, "delta": onto - raw}
    (out_dir / "ablation.json").write_text(json.dumps({"questions": rows, "summary": summary}, indent=2, default=str))
    return summary


def run_ontology_only(questions, ontology_arm, out_dir) -> dict:
    """Live-internals configuration (spec Amendment 3): run only the Auto
    Ontology arm. The raw-schema arm is not rerun; its rows stay null and
    the results document cites the standing control from the default
    configuration run."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    missing = [k for k in REQUIRED_SETTINGS if k not in ontology_arm.settings]
    if missing:
        raise ValueError(f"generation settings lack {missing}")
    generation = {"model": ontology_arm.model, "settings": dict(ontology_arm.settings)}
    # Ground truth is fixed on disk before any model is asked.
    (out_dir / "ground_truth.json").write_text(json.dumps([
        {"id": q["id"], "answer_type": q["answer_type"], "expected": q["expected"],
         "reference_sql": q.get("reference_sql")}
        for q in questions
    ], indent=2))
    (out_dir / "generation_settings.json").write_text(json.dumps(generation, indent=2))
    rows = []
    for q in questions:
        rows.append({
            "id": q["id"],
            "question": q.get("question"),
            "answer_type": q["answer_type"],
            "conflict_ids": q.get("conflict_ids", []),
            "expected": q["expected"],
            "ontology": _ask(ontology_arm, q, record_provenance=True),
            "raw": None,
        })
    summary = {"total": len(rows),
               "ontology_correct": sum(r["ontology"]["correct"] for r in rows),
               "raw_correct": None, "delta": None,
               "arms": "ontology only (live-internals configuration, spec Amendment 3); "
                       "the raw-schema control arm was not rerun"}
    (out_dir / "ablation.json").write_text(json.dumps({"questions": rows, "summary": summary}, indent=2, default=str))
    return summary
