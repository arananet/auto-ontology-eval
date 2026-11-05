"""S5: write RESULTS.md from run artifacts only.

Reads environment.json, smoke/smoke.json, timing.json, reconciliation.json,
generation_settings.json, ablation.json, equivalents.json and failure.json
from the run directory. A section whose artifact is absent says "No run evidence"; it
never estimates.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import equivalents
from .secrets import redact

NO_EVIDENCE = "No run evidence: the run did not produce `{}`."

LIMITS = [
    "- All data is synthetic: 8 small tables (dozens of rows) across one Postgres and one DuckDB "
    "source, built from fixed seed files. Results say nothing about scale, data volume or real "
    "enterprise schemas.",
    "- The fixture plants four conflicts only (net_sales semantics, location identity, product "
    "hierarchy, shared SKU identity). Other conflict kinds (units of measure, currencies, time "
    "zones, slowly changing dimensions, fiscal calendars) were not exercised.",
    "- 12 questions, each answered once per arm with one fixed chat model and fixed generation "
    "settings. Run-to-run variance, other models and prompt variants were not tested.",
    "- Only the default hosted NIM configuration was used; self-hosted NIMs, other connectors and "
    "the web UI workflows were not exercised.",
    "- The MCP surface was probed (tools listing) but agents using the MCP tools end to end were "
    "not tested.",
    "- Security, access control, multi-user behaviour, cost and latency beyond the measured time to "
    "first ontology were not covered.",
]


def _load(run_dir: Path, rel: str):
    path = run_dir / rel
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


def _fence(text: str, lang: str = "text") -> list[str]:
    fence = "```"
    while fence in text:
        fence += "`"
    return [f"{fence}{lang}", text, fence]


def _cell(value) -> str:
    if value is None:
        return "(no answer)"
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def _yes(b) -> str:
    return "yes" if b else "no"


def _environment(run_dir: Path) -> list[str]:
    out = ["## Environment", ""]
    env = _load(run_dir, "environment.json")
    if not env:
        return out + [NO_EVIDENCE.format("environment.json"), ""]
    labels = [
        ("runner", "Runner"), ("github_run_id", "GitHub run id"),
        ("upstream_repo", "Upstream repository"), ("upstream_commit", "Upstream commit"),
        ("chat_model", "Chat model"), ("embedding_model", "Embedding model"),
        ("rerank_model", "Rerank model"), ("run_date", "Run date"),
    ]
    for key, label in labels:
        if env.get(key):
            out.append(f"- {label}: `{env[key]}`")
    out.append("")
    smoke = _load(run_dir, "smoke/smoke.json")
    out.append("### Stack smoke (S1)")
    out.append("")
    if not smoke:
        out.append(NO_EVIDENCE.format("smoke/smoke.json"))
    else:
        for name, rec in smoke.items():
            ev = f" (evidence `smoke/{rec['evidence']}`)" if rec.get("evidence") else ""
            out.append(f"- {name}: {'pass' if rec.get('ok') else 'FAIL'}{ev}")
    return out + [""]


def _timing(run_dir: Path) -> list[str]:
    out = ["## Time to first ontology", ""]
    t = _load(run_dir, "timing.json")
    if not t or t.get("seconds") is None:
        return out + [NO_EVIDENCE.format("timing.json"), ""]
    out.append(f"- {t['seconds']} s from both sources registered to the first complete catalog export.")
    for key in ("start", "end"):
        if t.get(key):
            out.append(f"- {key}: `{t[key]}`")
    return out + [""]


def _reconciliation(run_dir: Path) -> list[str]:
    out = ["## Reconciliation checklist", ""]
    rec = _load(run_dir, "reconciliation.json")
    if not rec:
        return out + [NO_EVIDENCE.format("reconciliation.json"), ""]
    rows = rec["marks"] if isinstance(rec, dict) else rec
    counted = sum(1 for r in rows if r.get("counted"))
    out.append(f"{len(rows)} planted conflicts; {counted} marks backed by a verbatim catalog quote. "
               "A mark without a verbatim quote does not count.")
    out.append("")
    for r in rows:
        out.append(f"### {r['conflict_id']}: {r['mark']} (counted: {_yes(r.get('counted'))})")
        out.append("")
        if r.get("quote"):
            out += ["Quote from the exported catalog:", ""] + _fence(r["quote"]) + [""]
        else:
            out += ["No quote: the catalog had no text to cite for this conflict.", ""]
    return out


def _questions(run_dir: Path) -> list[str]:
    out = ["## Per-question results", ""]
    data = _load(run_dir, "ablation.json")
    if not data:
        return out + [NO_EVIDENCE.format("ablation.json"), ""]
    gen = _load(run_dir, "generation_settings.json")
    if gen:
        out += [f"Both arms: model `{gen['model']}`, settings `{json.dumps(gen['settings'], sort_keys=True)}`.", ""]
    out += [
        "| id | expected | Auto Ontology answer | correct | provenance | raw-schema answer | correct |",
        "|---|---|---|---|---|---|---|",
    ]
    for q in data["questions"]:
        o, r = q["ontology"], q["raw"]
        out.append(f"| {q['id']} | {_cell(q['expected'])} | {_cell(o.get('value'))} | {_yes(o.get('correct'))} "
                   f"| {_yes(o.get('provenance'))} | {_cell(r.get('value'))} | {_yes(r.get('correct'))} |")
    s = data["summary"]
    out += [
        "",
        f"- Auto Ontology arm: {s['ontology_correct']} / {s['total']} correct",
        f"- Raw-schema arm: {s['raw_correct']} / {s['total']} correct",
        f"- Delta (Auto Ontology minus raw schema): {s['delta']:+d}",
        "",
    ]
    return out


def _gallery(run_dir: Path) -> list[str]:
    out = ["## Failure gallery", ""]
    data = _load(run_dir, "ablation.json")
    if not data:
        return out + [NO_EVIDENCE.format("ablation.json"), ""]
    any_fail = False
    for q in data["questions"]:
        for arm, label in (("ontology", "Auto Ontology arm"), ("raw", "raw-schema arm")):
            a = q[arm]
            if a.get("correct"):
                continue
            any_fail = True
            out += [f"### {q['id']}, {label}", "",
                    f"- expected: {_cell(q['expected'])}", f"- got: {_cell(a.get('value'))}"]
            if a.get("error"):
                out.append(f"- error: {_cell(a['error'])}")
            out.append("")
            if a.get("sql"):
                out += ["Generated SQL, verbatim:", ""] + _fence(a["sql"], "sql") + [""]
            else:
                out += ["No SQL was produced.", ""]
    if not any_fail:
        out += ["Every answer in both arms was correct; no failures to show.", ""]
    return out


def _equivalents(run_dir: Path) -> list[str]:
    out = ["### Equivalents used instead of the literal spec step", ""]
    entries = equivalents.load(run_dir)
    if entries is None:
        return out + [NO_EVIDENCE.format(equivalents.FILENAME)
                      + " Whether the run used equivalents is not known.", ""]
    if not entries:
        return out + ["The run recorded no equivalents: every step it reached ran as the spec states.", ""]
    out += ["Each entry is a place where the run did something other than the literal step in S1 to S4.", ""]
    for e in entries:
        e = e if isinstance(e, dict) else {}
        reason = str(e.get("reason") or "").strip() or "reason not recorded"
        out.append(f"- {e.get('scenario') or 'scenario not recorded'}: "
                   f"{e.get('equivalent') or 'equivalent not recorded'}, "
                   f"instead of {e.get('literal') or 'literal step not recorded'}. Why: {reason}.")
    return out + [""]


def _limits(run_dir: Path) -> list[str]:
    return (["## Limits", "",
             "This is what the fixture did not exercise. No claim here goes beyond it.", ""] + LIMITS + [""]
            + _equivalents(run_dir))


def write_results(run_dir, out_path, secret: str | None = None) -> str:
    run_dir = Path(run_dir)
    lines = ["# RESULTS: NVIDIA Auto Ontology enterprise evaluation", "",
             "Internal evidence artifact, written by the harness from run artifacts only. Not for publication.", ""]
    failure = _load(run_dir, "failure.json")
    if failure:
        lines += [f"**Run stopped** at step `{failure.get('step')}`: {failure.get('reason')}", "",
                  "Sections after the failed step have no run evidence; nothing below is estimated.", ""]
    for part in (_environment(run_dir), _timing(run_dir), _reconciliation(run_dir),
                 _questions(run_dir), _gallery(run_dir), _limits(run_dir)):
        lines += part
    text = redact("\n".join(lines).rstrip() + "\n", secret)
    Path(out_path).write_text(text, encoding="utf-8")
    return text
