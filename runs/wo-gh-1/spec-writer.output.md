I made no edits. The spec for this work order already exists at `.openspec/specs/auto-ontology-enterprise-eval/spec.md` (in the project repo, one level above `.anvil-factory`) and already covers everything the work order asks for. Changing it would only add churn.

**Why it needs no changes**
- **Scenarios:** S1 to S5 match the work order. S1 is the pinned commit with three smoke checks. S2 is the two-source fixture with 8 to 10 tables, fixed seeds, ground truths stored in the fixture, and a checklist of four conflicts. S3 scores each conflict as detected, reconciled or ignored, each backed by a verbatim quote. S4 runs 12 questions through both arms, scores exact answers, records the delta and whether each answer has provenance, and saves the SQL verbatim. S5 builds `RESULTS.md` from the run only and lists every place the run used a substitute step.
- **Requirements:** the pinned upstream commit, synthetic data only, the key taken only from the `NVIDIA_API_KEY` secret, stopping on any missing evidence, the same model settings in both arms, and nothing published.
- **Chat model:** the spec owner recorded Amendment 2 on 2026-11-05. It pins `nvidia/nemotron-3.5-lightning-30b-a3b`, the only remaining candidate that answered when both were tried against the hosted endpoint. The two result files it cites exist under `runs/probes/`. Code and tests use the same pin: `src/auto_ontology_eval/config.py:12` and `tests/_support.py:27`.
- **Work order wording:** the work order still names `nvidia/nemotron-3-nano-30b-a3b`. The hosted endpoint retired that model and now returns HTTP 410 for it. Per the amendments, the spec governs over the work order text.

**Still open (for other stations, not this one)**
1. **Approval:** the spec header still says `Status: draft`, but the work order calls it approved. I left it alone because I can't approve my own work. The spec owner or the review station should change it.
2. **Work order text:** the work order's owner should update it to the Amendment 2 model. Amendment 1 says the work order is stale and that "the harness uses the new pin", but Amendment 2 doesn't repeat that. It would be clearer if the spec owner added one line to Amendment 2 saying it also overrides the work order text. I didn't write that line myself, because an amendment is the owner's record.
{"model": "claude-opus-5-5"}
