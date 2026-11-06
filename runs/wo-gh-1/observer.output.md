I couldn't observe anything for wo-gh-1, so I wrote `runs/wo-gh-1/observer.report.md` saying what's missing instead of reporting results.

- **No release record:** the deployer step is only `packet_ready`, and no release record exists.
- **Nothing in the repo for this work order:**
  - The spec `.openspec/specs/auto-ontology-enterprise-eval/spec.md` isn't there.
  - A repo-wide search finds no mention of `auto-ontology`.
  - There is no fixture, Compose file, workflow, ablation harness or `RESULTS.md`.
  - Nothing shows S1–S5 were ever run.
- **Run directory belongs to another job:** the existing `runs/wo-gh-1/` files describe an older "project design systems" work order that also used the id `wo-gh-1`. I did not use them as evidence and left the existing `observer.output.md` alone.

The report lists what's needed to proceed: the release record, the spec and builder output, the Actions run logs and `RESULTS.md`, and a fix for the id collision. I haven't committed anything.
{"model": "claude-sonnet-5-5"}
