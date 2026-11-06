I didn't change the spec. It already exists and is up to date, so I didn't rewrite or approve it. There's one path problem that the next stations need to know about.

**Where the spec is:** `/home/runner/work/auto-ontology-eval/auto-ontology-eval/.openspec/specs/auto-ontology-enterprise-eval/spec.md`. That's the project repo's root. It is not inside this working directory, `.anvil-factory/`, which holds the factory's own specs. The earlier reviewer-spec run failed because it looked in `.anvil-factory/.openspec/` and concluded the spec was missing (`runs/wo-gh-1/reviewer-spec.output.md`). That same run noted the builder had built a design-system feature in the factory instead of this evaluation. Every later station should resolve the spec, `src/`, `fixture/` and `tests/` against the project root, not the factory checkout.

**How the spec matches the work order:**
- **S1 to S5:** every work order item has a matching scenario, and some are stricter. S2 requires a checklist file listing the four planted conflicts. S4 defines exact matching (numbers equal after rounding to 2 decimals, value sets equal in any order). S5 has to name each step where the run used a substitute.
- **Rules beyond the work order:** the run stops with an error if the `NVIDIA_API_KEY` secret is missing or any step produces no evidence. Both S4 arms must use the same generation settings. The key must never appear in code, logs or `RESULTS.md`.
- **Chat model:** the work order still names `nvidia/nemotron-3-nano-30b-a3b`. Amendments 1 and 2 replaced it with `nvidia/nemotron-3.5-lightning-30b-a3b`: the original model was retired (HTTP 410), and the first replacement returned HTTP 404 on this account. Both are recorded with run evidence. S3 now names the new model, and Amendment 1 says the amendment governs over the work order text.
- **Second configuration:** Amendment 3 adds a `live-internals` run. It goes beyond this work order, but the owner decided it and recorded it inside the spec.

**Code check:** `src/auto_ontology_eval/config.py` and `tests/_support.py` use the same upstream commit and the same chat, embedding and reranking models as the spec. `fixture/questions.json` holds 12 questions, and `fixture/checklist.json` lists the planted conflicts.

**For approval:** the spec header still says `Status: draft`, while the work order calls it approved. Changing that line is a decision for the approver station or the spec owner, not me.

**Nothing is missing:** the work order and the existing spec cover everything this station needs.
{"model": "claude-opus-5-5"}
