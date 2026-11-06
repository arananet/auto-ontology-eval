"""S5: write RESULTS.md from run artifacts only.

Reads environment.json, smoke/smoke.json, timing.json, reconciliation.json,
generation_settings.json, ablation.json, equivalents.json and failure.json
from the run directory. A section whose artifact is absent says "No run evidence"; it
never estimates.
"""
from __future__ import annotations

import json
import re
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


# --- Live-internals configuration (spec Amendment 3) ------------------------

_DESCRIPTION_LINE = re.compile(r"^\s*description:\s*(.*?)\s*$")


def description_coverage(catalog_text: str) -> dict:
    """Count an exported catalog's description fields: authored (a real
    definition), blank (an empty value) or template (the upstream's own
    templated lines, "Business entity represented by table ..." and
    "format: ..." notes). This is the counting rule the S4 diagnosis used
    on the default catalog (88 fields: 77 blank, 11 template, 0 authored).
    """
    counts = {"total": 0, "authored": 0, "blank": 0, "template": 0}
    for line in catalog_text.splitlines():
        m = _DESCRIPTION_LINE.match(line)
        if not m:
            continue
        counts["total"] += 1
        value = m.group(1).strip().strip("'\"")
        if not value:
            counts["blank"] += 1
        elif value.startswith("Business entity represented by table") or value.startswith("format:"):
            counts["template"] += 1
        else:
            counts["authored"] += 1
    return counts


LIVE_LIMITS = [
    "- All data is synthetic: 8 small tables (dozens of rows) across one Postgres and one DuckDB "
    "source, built from fixed seed files. Results say nothing about scale, data volume or real "
    "enterprise schemas.",
    "- The fixture plants four conflicts only (net_sales semantics, location identity, product "
    "hierarchy, shared SKU identity). Other conflict kinds (units of measure, currencies, time "
    "zones, slowly changing dimensions, fiscal calendars) were not exercised.",
    "- 12 questions, each answered once by the Auto Ontology arm with one fixed chat model and "
    "fixed generation settings. Run-to-run variance, other models and prompt variants were not "
    "tested.",
    "- The raw-schema control arm was not rerun in this configuration (spec Amendment 3). The "
    "standing control result from the default configuration run is cited in the comparison "
    "section, and the comparison inherits that run's single-sample limits.",
    "- This configuration wires the stack's internal chat model slots to the evaluation's "
    "pinned chat model. It measures a configured stack, not the out-of-the-box default; the "
    "default configuration's measurement stands separately in runs/eval/RESULTS.md.",
    "- Only the hosted NIM configuration was used; self-hosted NIMs, other connectors and "
    "the web UI workflows were not exercised.",
    "- The MCP surface was probed (tools listing) but agents using the MCP tools end to end were "
    "not tested.",
    "- Security, access control, multi-user behaviour, cost and latency beyond the measured time to "
    "first ontology were not covered.",
]


def _default_dir(run_dir: Path) -> Path:
    """The frozen default configuration evidence directory (runs/eval)."""
    return Path(run_dir).parent / "eval"


def _live_environment(run_dir: Path) -> list[str]:
    out = _environment(run_dir)
    env = _load(run_dir, "environment.json")
    if env and env.get("configuration"):
        out += [f"- Configuration: `{env['configuration']}`", ""]
    models = _load(run_dir, "smoke/models.json")
    if models:
        out += ["### Internal models resolved in the running stack (S1)", ""]
        for name in sorted(models):
            out.append(f"- {name}: `{models[name]}`")
        out.append("")
    return out


def _live_timing(run_dir: Path) -> list[str]:
    out = _timing(run_dir)
    default_dir = _default_dir(run_dir)
    t = _load(default_dir, "timing.json")
    env = _load(default_dir, "environment.json")
    if t and t.get("seconds") is not None and env:
        out += [f"- Default configuration: {t['seconds']} s (GitHub Actions run "
                f"{env.get('github_run_id')}, `runs/eval/timing.json`).", ""]
    return out


def _coverage(run_dir: Path) -> list[str]:
    out = ["## Catalog description coverage", "",
           "Description fields are the `description:` lines of the exported catalog. A field is "
           "authored when it carries a real definition, blank when its value is empty, and "
           "template when it is one of the upstream's own templated lines (\"Business entity "
           "represented by table ...\" or a \"format: ...\" note).", ""]
    live_path = Path(run_dir) / "catalog.yaml"
    if not live_path.is_file():
        return out + [NO_EVIDENCE.format("catalog.yaml"), ""]
    live = description_coverage(live_path.read_text(encoding="utf-8"))
    out.append(f"- Live-internals catalog: {live['total']} description fields: "
               f"{live['authored']} authored, {live['blank']} blank, {live['template']} template.")
    default_path = _default_dir(run_dir) / "catalog.yaml"
    if default_path.is_file():
        frozen = description_coverage(default_path.read_text(encoding="utf-8"))
        out.append(f"- Default configuration catalog (`runs/eval/catalog.yaml`): "
                   f"{frozen['total']} description fields: {frozen['authored']} authored, "
                   f"{frozen['blank']} blank, {frozen['template']} template.")
    return out + [""]


def _live_reconciliation(run_dir: Path) -> list[str]:
    out = _reconciliation(run_dir)
    default_dir = _default_dir(run_dir)
    rec = _load(default_dir, "reconciliation.json")
    env = _load(default_dir, "environment.json")
    if rec and env:
        rows = rec["marks"] if isinstance(rec, dict) else rec
        marks = ", ".join(f"{r['conflict_id']} {r['mark']}" for r in rows)
        out += [f"- Default configuration (GitHub Actions run {env.get('github_run_id')}): {marks}.", ""]
    return out


def _live_questions(run_dir: Path) -> list[str]:
    out = ["## Per-question results (Auto Ontology arm)", ""]
    data = _load(run_dir, "ablation.json")
    if not data:
        return out + [NO_EVIDENCE.format("ablation.json"), ""]
    gen = _load(run_dir, "generation_settings.json")
    if gen:
        out += [f"Auto Ontology arm: model `{gen['model']}`, settings "
                f"`{json.dumps(gen['settings'], sort_keys=True)}`. The raw-schema arm was not "
                "rerun in this configuration.", ""]
    out += [
        "| id | expected | Auto Ontology answer | correct | provenance | SQL produced |",
        "|---|---|---|---|---|---|",
    ]
    for q in data["questions"]:
        o = q["ontology"]
        out.append(f"| {q['id']} | {_cell(q['expected'])} | {_cell(o.get('value'))} | "
                   f"{_yes(o.get('correct'))} | {_yes(o.get('provenance'))} | "
                   f"{_yes(bool(o.get('sql')))} |")
    s = data["summary"]
    with_sql = sum(1 for q in data["questions"] if q["ontology"].get("sql"))
    with_prov = sum(1 for q in data["questions"] if q["ontology"].get("provenance"))
    out += [
        "",
        f"- Auto Ontology arm: {s['ontology_correct']} / {s['total']} correct",
        f"- Questions where the arm produced SQL: {with_sql} / {s['total']}",
        f"- Answers carrying provenance: {with_prov} / {s['total']}",
        "",
    ]
    return out


def _live_comparison(run_dir: Path) -> list[str]:
    out = ["## Comparison with the default configuration and the standing control", ""]
    live = _load(run_dir, "ablation.json")
    if not live:
        return out + [NO_EVIDENCE.format("ablation.json"), ""]
    env = _load(run_dir, "environment.json") or {}
    s = live["summary"]
    out.append(f"- Live-internals Auto Ontology arm: {s['ontology_correct']} / {s['total']} "
               f"correct (this run, GitHub Actions run {env.get('github_run_id')}).")
    default_dir = _default_dir(run_dir)
    frozen = _load(default_dir, "ablation.json")
    denv = _load(default_dir, "environment.json")
    if not frozen or not denv:
        return out + [NO_EVIDENCE.format("runs/eval/ablation.json"), ""]
    d = frozen["summary"]
    rid = denv.get("github_run_id")
    out.append(f"- Default configuration Auto Ontology arm: {d['ontology_correct']} / "
               f"{d['total']} correct (GitHub Actions run {rid}, `runs/eval/ablation.json`).")
    out.append(f"- Raw-schema control arm, not rerun (spec Amendment 3): {d['raw_correct']} / "
               f"{d['total']} correct (GitHub Actions run {rid}, `runs/eval/ablation.json`).")
    lgen = _load(run_dir, "generation_settings.json")
    dgen = _load(default_dir, "generation_settings.json")
    if lgen and dgen:
        if lgen.get("model") == dgen.get("model") and lgen.get("settings") == dgen.get("settings"):
            out.append(f"- Both ablation records used model `{lgen['model']}` with settings "
                       f"`{json.dumps(lgen['settings'], sort_keys=True)}`; the standing control "
                       "is comparable on model and settings.")
        else:
            out.append(f"- Generation records differ: live `{lgen}`, default `{dgen}`.")
    out += [
        f"- Delta (live-internals Auto Ontology minus standing raw-schema control): "
        f"{s['ontology_correct'] - d['raw_correct']:+d}",
        f"- Delta (live-internals minus default configuration, Auto Ontology arm): "
        f"{s['ontology_correct'] - d['ontology_correct']:+d}",
        "",
    ]
    return out


def _live_gallery(run_dir: Path) -> list[str]:
    out = ["## Failure gallery", ""]
    data = _load(run_dir, "ablation.json")
    if not data:
        return out + [NO_EVIDENCE.format("ablation.json"), ""]
    any_fail = False
    for q in data["questions"]:
        a = q["ontology"]
        if a.get("correct"):
            continue
        any_fail = True
        out += [f"### {q['id']}, Auto Ontology arm", "",
                f"- expected: {_cell(q['expected'])}", f"- got: {_cell(a.get('value'))}"]
        if a.get("error"):
            out.append(f"- error: {_cell(a['error'])}")
        if a.get("response"):
            out.append(f"- response: {_cell(a['response'])}")
        out.append("")
        if a.get("sql"):
            out += ["Generated SQL, verbatim:", ""] + _fence(a["sql"], "sql") + [""]
        else:
            out += ["No SQL was produced.", ""]
    if not any_fail:
        out += ["Every Auto Ontology answer was correct; no failures to show.", ""]
    return out


def _live_limits(run_dir: Path) -> list[str]:
    return (["## Limits", "",
             "This is what the fixture did not exercise. No claim here goes beyond it.", ""]
            + LIVE_LIMITS + [""] + _equivalents(run_dir))


def write_live_results(run_dir, out_path, secret: str | None = None) -> str:
    """RESULTS-LIVE.md (spec Amendment 3): the live-internals run's own
    artifacts, plus the standing control and default configuration
    figures cited from the frozen runs/eval/ artifacts."""
    run_dir = Path(run_dir)
    lines = ["# RESULTS-LIVE: NVIDIA Auto Ontology enterprise evaluation, live-internals configuration", "",
             "Internal evidence artifact, written by the harness from run artifacts only. Not for publication.", "",
             "Second configuration under spec Amendment 3: identical to the default configuration "
             "except that the stack's internal chat model slots (DEFAULT_MODELS_MODEL, "
             "REASONING_MODEL, NON_REASONING_MODEL) are wired to the pinned chat model. The "
             "default configuration's results stand in runs/eval/RESULTS.md; this run does not "
             "modify them.", ""]
    failure = _load(run_dir, "failure.json")
    if failure:
        lines += [f"**Run stopped** at step `{failure.get('step')}`: {failure.get('reason')}", "",
                  "Sections after the failed step have no run evidence; nothing below is estimated.", ""]
    for part in (_live_environment(run_dir), _live_timing(run_dir), _coverage(run_dir),
                 _live_reconciliation(run_dir), _live_questions(run_dir),
                 _live_comparison(run_dir), _live_gallery(run_dir), _live_limits(run_dir)):
        lines += part
    text = redact("\n".join(lines).rstrip() + "\n", secret)
    Path(out_path).write_text(text, encoding="utf-8")
    return text
