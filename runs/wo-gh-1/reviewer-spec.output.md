I wrote the review to `runs/wo-gh-1/reviewer-spec.review.json` with verdict **fail**, and it parses as valid JSON.

- **Spec missing:** `.openspec/specs/auto-ontology-enterprise-eval/spec.md` doesn't exist, and nothing in the repo references that slug. I checked against the work order's S1–S5 text instead.
- **Wrong feature built:** `runs/wo-gh-1/builder.output.md` describes the project design system (`anvil/design.py`, the reviewer-design station). None of it relates to the Auto Ontology evaluation.
- **S1–S5 not met:** I found no Docker Compose or smoke evidence for S1, no two-source fixture for S2, no ontology generation run or conflict checklist for S3, and no 12-question ablation for S4. There is no `RESULTS.md` for S5 either.

The builder needs to rerun against the real spec, and the spec file needs to be present at the stated path.
{"model": "claude-sonnet-5-5"}
