"""Live steps that drive the real stack on the runner.

Each stage is ``fn(run_dir, api_key) -> Path`` of the evidence file it
wrote, for pipeline.run_all. Integration facts about the pinned upstream
(cdaf61e1) that these stages rely on:

- FastAPI on :3001 has no auth (README, server/identity.py).
- Health: GET /api/health (server/health/router.py).
- DuckDB is only connectable through CONNECTION_STRINGS
  (connectors/connection_string_factory.py has no duckdb type), so both
  sources are registered that way, and a compose override mounts the file.
- Ontology compilation runs only when frontend.configurations has
  semantic_compilation_enabled = 'true' (ingestion_service/config.py). The
  harness writes that row with SQL instead of building and driving the UI,
  then calls POST /api/semantic-compilation/trigger.
- Catalog export: POST /api/model/export (YAML, model_interchange/router.py).
- Chat: POST /api/chat/completions, server-sent events (chat/router.py).
- MCP is not in compose and requires a frontend OAuth token; the harness
  lists tools in process (mcp/tests/test_server.py does the same) and also
  records the unauthenticated HTTP response.

These stages need Docker and network access and are not unit tested.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import secrets as _pysecrets
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from . import ablation, config, equivalents, errors, fixture, reconcile, smoke, timing, upstream
from .secrets import redact

API = "http://localhost:3001"
INGEST = "http://localhost:3002"
FIXTURE_DB = "sales_mart"
DUCKDB_NAME = "ops_mart.duckdb"
CONTAINER_DATA = "/fixture-data"


class Context:
    upstream_dir: Path = Path("/tmp/auto-ontology")
    pg_password: str = ""
    configuration: str = "default"


CTX = Context()


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _run(cmd, key, cwd=None, timeout=1800, check=True, input_text=None) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, input=input_text)
    out = redact((proc.stdout or "") + (proc.stderr or ""), key)
    if check and proc.returncode != 0:
        raise errors.StepFailed(f"{' '.join(cmd[:4])} exited {proc.returncode}: {out[-2000:]}")
    return out


def _http(method, url, key, body=None, headers=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, redact(resp.read().decode("utf-8", "replace"), key)
    except urllib.error.HTTPError as exc:
        return exc.code, redact(exc.read().decode("utf-8", "replace"), key)


def _write(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = obj if isinstance(obj, str) else json.dumps(obj, indent=2, default=str)
    path.write_text(text, encoding="utf-8")
    return path


def _events(run_dir: Path) -> list:
    path = run_dir / "events.json"
    return json.loads(path.read_text()) if path.is_file() else []


def _event(run_dir: Path, **fields) -> None:
    ev = _events(run_dir)
    ev.append({**fields, "at": fields.get("at") or _now()})
    _write(run_dir / "events.json", ev)


# --- preflight -------------------------------------------------------------

def stage_preflight(run_dir: Path, key: str) -> Path:
    """Check that each pinned hosted model answers, before a long stack
    build. The spec forbids substituting another model, so a retired model
    stops the run here."""
    auth = {"Authorization": f"Bearer {key}"}
    checks = {
        "chat": ("POST", f"{config.NIM_BASE_URL}/chat/completions",
                 {"model": config.CHAT_MODEL, "messages": [{"role": "user", "content": "Reply OK"}],
                  "max_tokens": 8, "temperature": 0.0}),
        "embedding": ("POST", f"{config.NIM_BASE_URL}/embeddings",
                      {"model": config.EMBEDDING_MODEL, "input": ["sku"], "input_type": "query"}),
        "rerank": ("POST", "https://ai.api.nvidia.com/v1/retrieval/nvidia/llama-nemotron-rerank-vl-1b-v2/reranking",
                   {"model": config.RERANK_MODEL, "query": {"text": "sku"}, "passages": [{"text": "sku"}]}),
    }
    record = {}
    for name, (method, url, body) in checks.items():
        status, text = _http(method, url, key, body, auth)
        record[name] = {"model": body["model"], "status": status, "response": text[:500]}
    path = _write(run_dir / "preflight.json", record)
    bad = {n: r for n, r in record.items() if r["status"] != 200}
    if bad:
        detail = "; ".join(f"{r['model']} HTTP {r['status']}: {r['response'][:200]}" for r in bad.values())
        raise errors.StepFailed(f"hosted model preflight failed: {detail}")
    return path


# --- S2 fixture --------------------------------------------------------------

def stage_fixture(run_dir: Path, key: str) -> Path:
    data_dir = run_dir / "fixture-data"
    data_dir.mkdir(parents=True, exist_ok=True)
    duck = fixture.build_duckdb(data_dir / DUCKDB_NAME)
    duck.chmod(0o644)
    sql = _write(data_dir / "source_a.sql", fixture.postgres_load_sql())
    record = {
        "tables": fixture.table_names(),
        "rows": {s: {t: len(fixture.seed_rows(s, t)) for t in ts} for s, ts in fixture.table_names().items()},
        "duckdb_sha256": hashlib.sha256(duck.read_bytes()).hexdigest(),
        "source_a_sql_sha256": hashlib.sha256(sql.read_bytes()).hexdigest(),
    }
    return _write(run_dir / "fixture.json", record)


# --- S1 stand up and smoke ---------------------------------------------------

def _env_file(repo: Path, key: str) -> str:
    lines = []
    for line in (repo / ".env.example").read_text().splitlines():
        name = line.split("=", 1)[0].strip()
        # Drop the template's placeholder keys, endpoints and model lines;
        # the nvapi- built-in endpoints apply and the model pins are written
        # explicitly below (the built-in chat default is end of life).
        if name.endswith("_API_KEY") or name.endswith("_MODEL") or name.endswith("_ENDPOINT"):
            continue
        if name in ("POSTGRES_PASSWORD", "AUTH_SECRET", "CONNECTION_STRINGS", "POSTGRES_PORT"):
            continue
        lines.append(line)
    lines += [
        f"NVIDIA_API_KEY={key}",
        "POSTGRES_PORT=5432",
        f"POSTGRES_PASSWORD={CTX.pg_password}",
        f"AUTH_SECRET={_pysecrets.token_hex(32)}",
        "CONNECTION_STRINGS="
        f"postgresql://postgres:{CTX.pg_password}@postgres:5432/{FIXTURE_DB},"
        f"duckdb://{CONTAINER_DATA}/{DUCKDB_NAME}",
    ]
    lines += [f"{name}={value}" for name, value in upstream.model_env(CTX.configuration).items()]
    return "\n".join(lines) + "\n"


def _override(run_dir: Path) -> Path:
    data = (run_dir / "fixture-data").resolve()
    text = "services:\n" + "".join(
        f"  {svc}:\n    volumes:\n      - {data}:{CONTAINER_DATA}:ro\n"
        for svc in ("auto-ontology", "ingestion-service")
    )
    return _write(run_dir / "compose.override.yml", text)


def _compose(*args, run_dir):
    return upstream.compose_command(CTX.upstream_dir, *args, overrides=[_override(run_dir)])


def _psql(sql: str, key: str, run_dir: Path, db: str = "auto_ontology") -> str:
    return _run(_compose("exec", "-T", "postgres", "psql", "-v", "ON_ERROR_STOP=1",
                         "-U", "postgres", "-d", db, run_dir=run_dir), key, input_text=sql)


def _wait(pred, timeout_s, every=5.0, what="condition"):
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        try:
            ok, last = pred()
            if ok:
                return last
        except Exception as exc:  # keep polling
            last = str(exc)
        time.sleep(every)
    raise errors.StepFailed(f"timed out waiting for {what}: {str(last)[:500]}")


def _mcp_tools_in_process(key: str) -> tuple[bool, str]:
    venv = CTX.upstream_dir.parent / "mcp-venv"
    if not venv.exists():
        _run([sys.executable, "-m", "venv", str(venv)], key)
        _run([str(venv / "bin" / "pip"), "install", "-q", str(CTX.upstream_dir / "mcp")], key, timeout=900)
    script = (
        "import asyncio, json\n"
        "from fastmcp import Client\n"
        "from auto_ontology_mcp import server, config as c\n"
        "s = c.Settings(api_url='http://localhost:3000', spec_path=c.DEFAULT_SPEC_PATH, host='127.0.0.1',"
        " port=3003, timeout_s=30.0, chat_timeout_s=900.0, public_url='http://127.0.0.1:3003')\n"
        "mcp, _ = server.build_server(s)\n"
        "async def main():\n"
        "    async with Client(mcp) as cl:\n"
        "        tools = await cl.list_tools()\n"
        "    print(json.dumps({'method': 'tools/list (in-process)', 'tools': [t.name for t in tools]}))\n"
        "asyncio.run(main())\n"
    )
    out = _run([str(venv / "bin" / "python"), "-I", "-c", script], key, check=False, timeout=300)
    try:
        tools = json.loads(out.strip().splitlines()[-1])["tools"]
    except Exception:
        return False, out
    return bool(tools), out


def stage_s1(run_dir: Path, key: str) -> Path:
    dest = CTX.upstream_dir
    # The upstream checkout receives the key-carrying Compose .env. The run
    # dir is the evidence that gets committed and uploaded, so refuse an
    # upstream dir inside it before anything is cloned or written (spec
    # Requirements, NVIDIA_API_KEY rule).
    if Path(dest).resolve().is_relative_to(Path(run_dir).resolve()):
        raise errors.StepFailed(
            "S1: the upstream dir is inside the run evidence directory; the Compose .env that "
            "carries the key must be written outside it (pass --upstream-dir outside the run dir)")
    CTX.pg_password = _pysecrets.token_hex(16)
    if not (dest / ".git").exists():
        for cmd in upstream.clone_commands(dest)[:2]:
            _run(cmd, key)
    upstream.verify_checkout(_run(upstream.clone_commands(dest)[2], key))
    env_text = _env_file(dest, key)
    (dest / ".env").write_text(env_text)
    (dest / ".env").chmod(0o600)
    _run(_compose("up", "-d", "postgres", run_dir=run_dir), key, cwd=dest)
    _wait(lambda: ("accepting" in _run(_compose("exec", "-T", "postgres", "pg_isready", "-U", "postgres",
                                                run_dir=run_dir), key, check=False), "pg_isready"),
          180, what="postgres")
    _psql(f"CREATE DATABASE {FIXTURE_DB};", key, run_dir, db="postgres")
    _psql((run_dir / "fixture-data" / "source_a.sql").read_text(), key, run_dir, db=FIXTURE_DB)
    _write(run_dir / "compose-up.log", _run(_compose("up", "-d", "--build", run_dir=run_dir), key,
                                            cwd=dest, timeout=3600))
    _wait(lambda: (_http("GET", f"{API}/api/health", key)[0] == 200, "health"), 900, what="API health")
    # Fail closed before any scenario evidence if the stack would call a
    # model other than the spec pins (S3 and both S4 arms depend on it).
    # In the live-internals configuration the verified slots include the
    # DEFAULT_MODELS fallback triplet (spec Amendment 3).
    resolved = upstream.verify_resolved_models(_run(
        _compose("exec", "-T", "auto-ontology", "python", "-c",
                 upstream.resolve_models_script(CTX.configuration),
                 run_dir=run_dir), key, cwd=dest, timeout=120), CTX.configuration)
    _write(run_dir / "smoke" / "models.json", resolved)

    def health():
        status, body = _http("GET", f"{API}/api/health", key)
        return status == 200, f"GET /api/health -> HTTP {status}\n{body}"

    def catalog():
        status, body = _http("GET", f"{API}/api/datasources/dbs", key)
        return status == 200, f"GET /api/datasources/dbs -> HTTP {status}\n{body}"

    def mcp():
        equivalents.record(
            run_dir, "S1",
            literal="MCP tools/list request sent over the network to the running MCP server",
            equivalent="MCP tools listed in process against the pinned MCP server module (fastmcp in-memory client)",
            reason="the pinned MCP server is not part of the upstream compose stack and its HTTP endpoint "
                   "requires a frontend OAuth token, which the harness has no way to obtain without the "
                   "interactive web login")
        ok, listing = _mcp_tools_in_process(key)
        return ok, ("Pinned MCP server requires a frontend OAuth token on HTTP; listing tools in process "
                    "(closest equivalent of tools/list):\n" + listing)

    smoke.run_smoke({"health": health, "catalog": catalog, "mcp": mcp}, run_dir, secret=key)
    return run_dir / "smoke" / "smoke.json"


# --- S3 generate and score ----------------------------------------------------

def _db_names(key):
    status, body = _http("GET", f"{API}/api/datasources/dbs", key)
    if status != 200:
        return set(), body
    text = body.lower()
    return {s for s, name in (("A", FIXTURE_DB), ("B", DUCKDB_NAME.split(".")[0])) if name in text}, body


def stage_s3(run_dir: Path, key: str) -> Path:
    seen = set()

    def both_registered():
        names, body = _db_names(key)
        for s in sorted(names - seen):
            _event(run_dir, event="source_registered", source=s)
            seen.add(s)
        return seen == {"A", "B"}, body

    _wait(both_registered, 1800, every=10, what="both sources ingested")
    _psql("INSERT INTO frontend.configurations(key, value, updated_at) VALUES "
          "('semantic_compilation_enabled', 'true', now()) ON CONFLICT (key) DO UPDATE "
          "SET value = 'true', updated_at = now();", key, run_dir)
    trigger_at = _dt.datetime.now(_dt.timezone.utc)
    status, body = _http("POST", f"{API}/api/semantic-compilation/trigger", key, {})
    _write(run_dir / "s3" / "trigger.txt", f"HTTP {status}\n{body}")
    if status >= 300:
        raise errors.StepFailed(f"compilation trigger HTTP {status}: {body[:300]}")

    def compiled():
        st, b = _http("GET", f"{API}/api/semantic-compilation/status", key)
        info = json.loads(b) if st == 200 else {}
        if info.get("last_failure_at") and not info.get("running") and not info.get("last_success_at"):
            raise errors.StepFailed(f"compilation failed: {b[:300]}")
        done = (st == 200 and not info.get("running") and info.get("last_success_at")
                and _dt.datetime.fromisoformat(info["last_success_at"].replace("Z", "+00:00")) >= trigger_at)
        return bool(done), b

    try:
        _write(run_dir / "s3" / "status.json", _wait(compiled, 3600, every=15, what="ontology compilation"))
    except errors.StepFailed:
        logs = _run(_compose("logs", "--tail", "200", "ingestion-service", run_dir=run_dir), key, check=False)
        _write(run_dir / "s3" / "ingestion-service.log", logs)
        raise
    status, catalog = _http("POST", f"{API}/api/model/export", key,
                            {"databases": [], "format": "auto_ontology"}, timeout=300)
    if status != 200 or not catalog.strip():
        raise errors.StepFailed(f"catalog export HTTP {status}: {catalog[:300]}")
    _write(run_dir / "catalog.yaml", catalog)
    _event(run_dir, event="catalog_exported", complete=True)
    seconds = timing.time_to_first_ontology(_events(run_dir))
    ev = _events(run_dir)
    _write(run_dir / "timing.json", {"seconds": round(seconds, 2),
                                     "start": max(e["at"] for e in ev if e["event"] == "source_registered"),
                                     "end": ev[-1]["at"]})
    checklist = fixture.load_checklist()
    marks = reconcile.classify(checklist, catalog)
    return _write(run_dir / "reconciliation.json", reconcile.score(checklist, catalog, marks))


# --- S4 ablation --------------------------------------------------------------

def _rows_value(rows, answer_type):
    if rows is None:
        return None
    if isinstance(rows, dict):
        rows = rows.get("rows") or rows.get("data") or [rows]
    cells = []
    for r in rows or []:
        if isinstance(r, dict):
            r = list(r.values())
        if isinstance(r, (list, tuple)) and r:
            cells.append(r[0])
        else:
            cells.append(r)
    if answer_type == "number":
        return cells[0] if len(cells) == 1 else None
    return [str(c) for c in cells] or None


PROVENANCE_KEYS = ("provenance", "lineage", "citation", "citations", "sources", "custom_analyses_used")


class OntologyArm:
    """Auto Ontology chat API. Model and settings are the upstream chat
    client's (see config.GENERATION_SETTINGS)."""

    def __init__(self, key, run_dir):
        self.model = config.CHAT_MODEL
        self.settings = dict(config.GENERATION_SETTINGS)
        self.key, self.run_dir = key, run_dir

    def ask(self, question):
        req = urllib.request.Request(
            f"{API}/api/chat/completions", method="POST",
            data=json.dumps({"question": question["question"], "evidence": None,
                             "conversation_id": None, "prediction": None}).encode(),
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"})
        events, sql = [], None
        with urllib.request.urlopen(req, timeout=900) as resp:
            for raw in resp:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    events.append(json.loads(payload))
                except ValueError:
                    continue
        _write(self.run_dir / "s4" / f"{question['id']}.ontology.events.json",
               redact(json.dumps(events, indent=2), self.key))
        result = next((e.get("answer") for e in reversed(events) if e.get("type") == "result"), None)
        for e in events:
            if e.get("type") == "sql":
                sql = e.get("sql")
        error = next((e for e in events if e.get("type") == "error"), None)
        if result is None:
            if error:
                partial = error.get("partial_answer") or {}
                return {"value": None, "sql": partial.get("sql_code") or sql,
                        "provenance": None, "response": error.get("message")}
            return {"value": None, "sql": sql, "provenance": None}
        prov = {k: result[k] for k in PROVENANCE_KEYS if result.get(k)}
        return {"value": _rows_value(result.get("sql_response_from_db"), question["answer_type"]),
                "sql": result.get("sql_code") or sql, "provenance": prov or None,
                "response": result.get("response")}


class RawSchemaArm:
    """Same hosted chat model, given only the raw DDL; its SQL runs on the
    fixture data (SQLite, A as schema a, B as schema b)."""

    def __init__(self, key, run_dir):
        self.model = config.CHAT_MODEL
        self.settings = dict(config.GENERATION_SETTINGS)
        self.key, self.run_dir = key, run_dir
        self.schema = fixture.raw_schema_text()

    def ask(self, question):
        prompt = ablation.raw_schema_prompt(question["question"], self.schema)
        status, body = _http("POST", f"{config.NIM_BASE_URL}/chat/completions", self.key,
                             {"model": self.model, "messages": [{"role": "user", "content": prompt}],
                              **self.settings}, {"Authorization": f"Bearer {self.key}"}, timeout=300)
        _write(self.run_dir / "s4" / f"{question['id']}.raw.response.json", body)
        if status != 200:
            raise errors.StepFailed(f"HTTP {status}: {body[:300]}")
        content = json.loads(body)["choices"][0]["message"]["content"] or ""
        start, end = content.find("{"), content.rfind("}")
        sql = json.loads(content[start:end + 1])["sql"] if start != -1 else None
        if not sql:
            return {"value": None, "sql": None}
        try:
            rows = fixture.reference_connection().execute(sql).fetchall()
        except Exception as exc:
            return {"value": None, "sql": sql, "error": str(exc)}
        return {"value": _rows_value([list(r) for r in rows], question["answer_type"]), "sql": sql}


def stage_s4(run_dir: Path, key: str) -> Path:
    if CTX.configuration == config.LIVE_CONFIGURATION:
        # Spec Amendment 3: in the live-internals configuration only the
        # Auto Ontology arm runs. The raw-schema control arm is not rerun;
        # its result from the default configuration run stands as the
        # control and RESULTS-LIVE.md cites it with that provenance.
        ablation.run_ontology_only(fixture.load_questions(), OntologyArm(key, run_dir), run_dir)
        return run_dir / "ablation.json"
    equivalents.record(
        run_dir, "S4",
        literal="raw-schema arm SQL executed on the live Postgres (Source A) and DuckDB (Source B) sources",
        equivalent="raw-schema arm SQL executed on an in-memory SQLite copy of the fixture, loaded from the "
                   "same seed files, with Source A as schema a and Source B as schema b",
        reason="the two live sources are separate engines, so one model-written query cannot join across "
               "them; a single SQLite copy holding both sources lets the raw-schema arm answer every "
               "question, including cross-source ones, with one query, and is the same engine the reference "
               "SQL ground truths were computed on")
    ablation.run(fixture.load_questions(), OntologyArm(key, run_dir), RawSchemaArm(key, run_dir), run_dir)
    return run_dir / "ablation.json"


def stage_teardown_logs(run_dir: Path, key: str) -> None:
    """Best effort: capture service logs (redacted) and stop the stack."""
    try:
        _write(run_dir / "compose-logs.txt",
               _run(_compose("logs", "--tail", "300", run_dir=run_dir), key, check=False))
        _run(_compose("down", "-v", run_dir=run_dir), key, check=False)
    except Exception:
        pass


STEPS = [
    ("preflight", stage_preflight),
    ("s2_fixture", stage_fixture),
    ("s1_smoke", stage_s1),
    ("s3_generate", stage_s3),
    ("s4_ablation", stage_s4),
]
