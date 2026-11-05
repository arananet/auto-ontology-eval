The spec for this work order already existed and covered all five scenarios, so I made two small edits to it instead of rewriting it. The edits are in the project repo at `.openspec/specs/auto-ontology-enterprise-eval/spec.md` (one level above `.anvil-factory`). I haven't committed them; that's left to the line.

**What I changed**
1. **S5 limits section:** RESULTS.md must now name every place where the run used a substitute for the step the spec describes in S1 to S4, and say why. The earlier spec review found two such cases, and the spec now names them:
   - the S1 MCP probe lists tools in process rather than over the network, because the MCP server at the pinned commit needs an OAuth token;
   - the raw-schema arm in S4 runs its SQL on a copy of the fixture, not on the live Postgres and DuckDB sources.
2. **Amendment 1:** added a note that the work order still quotes the old chat model `nvidia/nemotron-3-nano-30b-a3b`. That model was retired on 2026-09-01 and the hosted endpoint returns HTTP 410 for it. The amendment's pin, `nvidia/nemotron-nano-3-30b-a3b`, is the one that applies, and the harness already uses it.

Nothing else changed: the scenario ids S1 to S5, the upstream commit pin, and the embedding and reranking model pins are as they were.

**Still open**
- **Approval:** the work order says the spec is approved, but the file still says `Status: draft`. I left it that way because I can't approve my own edits; a separate station has to.
- **Model pin in the work order:** whoever owns the work order should update its text to the new pin, so the spec and the work order stop disagreeing.
{"model": "claude-opus-5-5"}
