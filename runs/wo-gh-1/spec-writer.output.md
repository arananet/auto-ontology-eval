I updated the existing spec at `.openspec/specs/auto-ontology-enterprise-eval/spec.md` in the project repo. The only section I changed is "Work order coverage", which doesn't set requirements. No requirement, scenario, amendment or status changed, and the status stays `draft`. Approval belongs to another station.

**Why a small change was enough:** the spec already covered all five things the work order asks for (S1–S5), and three amendments since then build on it. What was out of date was the coverage section. It still said the work order had been cut down to S1–S3 at intake. This intake accepted the whole work order (risk high), so S4 and S5 are back in scope.

**What the revised coverage section now says:**
- **Scope:** wo-gh-1 covers S1–S5 and every requirement. Amendment 3 (the second, "live-internals" model setup) is still not part of it, because the work order asks only for the default hosted NIM models.
- **Clause map:** each clause of the work order is matched to its scenario, and the "no real company data, nothing published" clause is matched to the requirements that say the same.
- **Chat model:** the work order still names `nvidia/nemotron-3-nano-30b-a3b`. That model was retired, and Amendment 2 replaced it with `nvidia/nemotron-3.5-lightning-30b-a3b` for S3 and for both S4 answer runs.
- **API key:** the work order's "secret only" rule is matched to the requirement that also keeps the key out of logs, committed files, uploaded artifacts and RESULTS.md.
- **"Same LLM":** the work order's "same LLM with raw schema only" is matched to the rule that both S4 runs use the same model id and the same generation settings, recorded in a run artifact.

**Decision needed before the builder starts:** the repo already has a full default-model run, GitHub Actions run 42127124473, saved in `runs/eval/` with its RESULTS.md. Amendment 3 treats that run as frozen and uses it as its baseline. The spec doesn't say whether this work order should:
- **(a)** accept that existing run as its S1–S5 evidence, or
- **(b)** run the evaluation again into a new run folder.

Running again into `runs/eval/` would overwrite the evidence Amendment 3 relies on. I listed this as an open question for the spec owner to settle with an amendment rather than guessing.

`git diff` also shows changes to files under `runs/wo-gh-1/`, `work_orders/wo-gh-1.json` and `line-output.log`. Those were already in the working tree from the intake step, not from me. My only edit is the spec file.
{"model": "claude-opus-5-5"}
