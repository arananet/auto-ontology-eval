I revised the existing spec at `.openspec/specs/auto-ontology-enterprise-eval/spec.md` in the project repo. I didn't create a new one. Scenario ids S1 to S5 and their scope are unchanged. The file is edited in the working tree and not committed; I'm leaving the commit to the line.

**What I changed**
- **New requirement, fail closed:** if the `NVIDIA_API_KEY` secret is missing or empty, or any step can't produce its evidence file, the run stops with a non-zero exit. RESULTS.md then records which step failed rather than filling in estimates.
- **New requirement, same settings in both S4 arms:** both arms use the same chat model id, temperature, max tokens and seed, and the run saves those settings to a file. Last time the reviewer couldn't check this.
- **S2:** the fixture must include a machine-readable checklist of at least four planted conflicts: net_sales meaning, plant and DC codes versus location names (with the mapping written into the fixture), product hierarchy, and shared SKUs. The reviewer couldn't check the contents of `conflicts.json` last time.
- **S3:** "time to first ontology" now has a definition: wall-clock time from both sources being registered to the first complete catalog export.
- **S4:** at least one question must touch each planted conflict. "Exact answer" now means numbers equal after rounding to 2 decimal places, and sets of values equal in any order. Anything else, including no answer, counts as wrong.

**Still open**
- **Approval:** the work order says the spec was approved, but the file still says `Status: draft`, and my edits need approval anyway. I left it as draft because I can't approve my own work; a separate approval station has to do that.
- **Two assumptions to confirm:** the 2-decimal rounding rule and "B uses a different grouping or none" for the product hierarchy are my choices. The work order doesn't specify Source B's hierarchy.
- **Old files:** the existing files in `runs/wo-gh-1/` come from an earlier run that ended in `changes_requested`. I used its spec review only to find what to tighten.
{"model": "claude-opus-5-5"}
