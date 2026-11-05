"""S3 reconciliation scoring against the planted-conflict checklist.

Every conflict gets exactly one mark: detected, reconciled or ignored. A
mark counts only when it carries a quote that appears verbatim (exact,
case-sensitive substring) in the exported catalog.

classify() is a fixed, deterministic rule set, written before any run:
a catalog sentence is relevant to a conflict when it names something from
the Source A side and something from the Source B side of that conflict
(table, column, or a location name/code from the ground-truth mapping).
A relevant sentence with mapping language marks the conflict reconciled;
one with conflict language marks it detected; otherwise it is ignored.
"""
from __future__ import annotations

import re

MARKS = ("detected", "reconciled", "ignored")

RECONCILE_WORDS = (
    "maps to", "mapped to", "mapping", "same as", "equivalent", "corresponds to",
    "correspond to", "joins to", "join key", "joined on", "reconcil", "crosswalk",
    "alias", "synonym", "same entity", "same product", "same location", "same sku",
)
DETECT_WORDS = (
    "conflict", "differ", "different", "inconsistent", "inconsisten", "discrepan",
    "ambigu", "mismatch", "unlike", "whereas", "in contrast", "contradict",
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+|\\n")


def _sides(conflict: dict) -> tuple[set[str], set[str]]:
    a, b = set(), set()
    for inv in conflict["involves"]:
        side = a if inv["source"] == "A" else b
        side.update({inv["table"], inv["column"]})
    for entry in conflict.get("ground_truth", {}).get("mapping", []) or []:
        a.add(entry["name"])
        b.add(entry["code"])
    shared = a & b
    return a - shared, b - shared


def _mentions(text: str, term: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", text, re.I) is not None


def _sentences(catalog: str) -> list[str]:
    out = []
    for piece in _SENTENCE_SPLIT.split(catalog):
        piece = piece.strip()
        if piece and piece in catalog:
            out.append(piece)
    return out


def classify(checklist: list[dict], catalog: str) -> list[dict]:
    sentences = _sentences(catalog)
    marks = []
    for conflict in checklist:
        a_terms, b_terms = _sides(conflict)
        relevant = [
            s for s in sentences
            if any(_mentions(s, t) for t in a_terms) and any(_mentions(s, t) for t in b_terms)
        ]
        mark, quote = "ignored", ""
        for words, label in ((RECONCILE_WORDS, "reconciled"), (DETECT_WORDS, "detected")):
            hit = next((s for s in relevant if any(w in s.lower() for w in words)), None)
            if hit:
                mark, quote = label, hit
                break
        if mark == "ignored":
            # Evidence of what the catalog does say about the involved names.
            quote = next(
                (s for s in sentences if any(_mentions(s, t) for t in a_terms | b_terms)), ""
            )
        marks.append({"conflict_id": conflict["id"], "mark": mark, "quote": quote})
    return marks


def score(checklist: list[dict], catalog: str, marks: list[dict]) -> list[dict]:
    ids = [c["id"] for c in checklist]
    seen: dict[str, dict] = {}
    for m in marks:
        cid = m.get("conflict_id")
        if cid not in ids:
            raise ValueError(f"mark for unknown conflict {cid!r}")
        if cid in seen:
            raise ValueError(f"conflict {cid!r} has more than one mark")
        if m.get("mark") not in MARKS:
            raise ValueError(f"unknown mark {m.get('mark')!r} for {cid!r}")
        seen[cid] = m
    missing = [c for c in ids if c not in seen]
    if missing:
        raise ValueError(f"conflicts without a mark: {missing}")
    scored = []
    for cid in ids:
        m = seen[cid]
        quote = m.get("quote") or ""
        counted = bool(quote.strip()) and quote in catalog
        scored.append({"conflict_id": cid, "mark": m["mark"], "quote": quote, "counted": counted})
    return scored
