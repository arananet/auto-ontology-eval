"""S2 fixture access: seed files, checklist, questions, reference database.

The fixture lives in <project>/fixture and is committed. Seed CSVs are the
only source of rows; every loader here reads them, nothing is generated at
run time. fixture/generate.py is the one-off script that wrote the seeds
from a fixed seed and is kept for transparency.

Reference SQL runs on SQLite (standard library) with Source A attached as
schema ``a`` and Source B as schema ``b``. That keeps the ground truth
recomputable without Postgres or DuckDB.
"""
from __future__ import annotations

import csv
import json
import re
import sqlite3
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixture"
SOURCE_DIRS = {"A": FIXTURE_DIR / "source_a", "B": FIXTURE_DIR / "source_b"}
SCHEMA_ALIAS = {"A": "a", "B": "b"}

_CREATE_RE = re.compile(r"create table\s+(?:if not exists\s+)?\"?(\w+)\"?", re.I)


def schema_sql(source: str) -> str:
    return (SOURCE_DIRS[source] / "schema.sql").read_text(encoding="utf-8")


def table_names() -> dict[str, list[str]]:
    """Tables per source, in DDL order."""
    return {s: _CREATE_RE.findall(schema_sql(s)) for s in SOURCE_DIRS}


def seed_path(source: str, table: str) -> Path:
    return SOURCE_DIRS[source] / "seeds" / f"{table}.csv"


def seed_rows(source: str, table: str) -> list[dict[str, str]]:
    with seed_path(source, table).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_checklist() -> list[dict]:
    raw = json.loads((FIXTURE_DIR / "checklist.json").read_text(encoding="utf-8"))
    return raw["conflicts"] if isinstance(raw, dict) else raw


def load_questions() -> list[dict]:
    raw = json.loads((FIXTURE_DIR / "questions.json").read_text(encoding="utf-8"))
    return raw["questions"] if isinstance(raw, dict) else raw


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    return "\n".join(line.split("--", 1)[0].rstrip() for line in sql.splitlines())


def _statements(sql: str) -> list[str]:
    return [s.strip() for s in _strip_comments(sql).split(";") if s.strip()]


def raw_schema_text() -> str:
    """DDL of both sources, comments removed: the raw arm's only context."""
    parts = []
    for source, label in (("A", "Source A (PostgreSQL)"), ("B", "Source B (DuckDB)")):
        body = ";\n\n".join(_statements(schema_sql(source))) + ";"
        parts.append(f"{label}:\n{body}")
    return "\n\n".join(parts) + "\n"


def reference_connection() -> sqlite3.Connection:
    """In-memory SQLite with A as schema ``a`` and B as schema ``b``."""
    conn = sqlite3.connect(":memory:")
    for source, alias in SCHEMA_ALIAS.items():
        conn.execute(f"ATTACH DATABASE ':memory:' AS {alias}")
        for stmt in _statements(schema_sql(source)):
            stmt = _CREATE_RE.sub(lambda m: f"CREATE TABLE {alias}.{m.group(1)}", stmt, count=1)
            conn.execute(stmt)
        for table in table_names()[source]:
            rows = seed_rows(source, table)
            if not rows:
                continue
            cols = list(rows[0].keys())
            sql = (
                f"INSERT INTO {alias}.{table} ({', '.join(cols)}) "
                f"VALUES ({', '.join('?' for _ in cols)})"
            )
            # Column affinity converts numeric strings to numbers.
            conn.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
    conn.commit()
    return conn


def build_duckdb(path: Path) -> Path:
    """Write Source B to a DuckDB file from its DDL and seed CSVs."""
    import duckdb  # only needed on the runner

    path = Path(path)
    if path.exists():
        path.unlink()
    con = duckdb.connect(str(path))
    try:
        for stmt in _statements(schema_sql("B")):
            con.execute(stmt)
        for table in table_names()["B"]:
            csv_path = str(seed_path("B", table)).replace("'", "''")
            con.execute(
                f'INSERT INTO "{table}" SELECT * FROM '
                f"read_csv('{csv_path}', header=true, all_varchar=true)"
            )
    finally:
        con.close()
    return path


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def postgres_load_sql() -> str:
    """DDL plus INSERTs for Source A, for psql. Every value is quoted;
    Postgres casts the literals to the declared column types."""
    lines = [s + ";" for s in _statements(schema_sql("A"))]
    for table in table_names()["A"]:
        rows = seed_rows("A", table)
        cols = list(rows[0].keys())
        values = ",\n".join(
            "(" + ", ".join(_sql_literal(r[c]) for c in cols) + ")" for r in rows
        )
        lines.append(f"INSERT INTO {table} ({', '.join(cols)}) VALUES\n{values};")
    return "\n\n".join(lines) + "\n"
