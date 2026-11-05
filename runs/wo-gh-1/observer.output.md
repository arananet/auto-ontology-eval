The observation report is at `runs/wo-gh-1/observer.output.md` in the project root, not in `.anvil-factory`. The `.anvil-factory/runs/wo-gh-1` folder holds an older, unrelated work order that reuses the id. I did not commit the file.

**The run's S3 and S4 results are not valid evidence about Auto Ontology.** I read the committed artifacts in `runs/eval/` from GitHub Actions run `42127124473` and re-ran nothing.

- **No release record:** There is only `deployer.packet.md` with status `packet_ready`, and no deployer output. The report covers the evidence the run left behind.
- **LLM calls failed inside the stack:** The compose logs show the Auto Ontology service calling `nvidia/nemotron-3-nano-30b-a3b`, the end-of-life default. Those calls returned `[410] Gone`, even though the spec pins `nvidia/nemotron-3.5-lightning-30b-a3b`.
- **Ontology generation (S3):** The "time to first ontology" of 15.42 s is largely the failures returning quickly. 77 of the 88 catalog descriptions are empty. All 4 planted conflicts are marked `ignored`, and each quote is just a table name, so those marks don't show how the tool treats conflicting definitions.
- **Ablation (S4):** The Auto Ontology arm answered 0 of 12, because every question ended at "LLM failed to produce a response." The raw-schema arm called the pinned model directly and scored 8 of 12. The reported delta of -8 compares a working model with a dead endpoint, so it doesn't measure the semantic layer.
- **RESULTS.md overstates the run:** It reports the 0/12 and the 4 `ignored` marks without saying the stack's LLM calls failed.

I did not confirm why the pin didn't take effect, but there is a likely cause. The committed `upstream.py` has no model pinning. The working tree has uncommitted changes that add `model_env()` and `verify_resolved_models()` and also edit `live.py`. I didn't check which version the run used.

The report recommends committing and reviewing those changes, failing the harness on any `[410]` or mostly empty descriptions, re-running S3 and S4, and treating the current `RESULTS.md` as invalid. Nothing should be published from it.
{"model": "claude-sonnet-5-5"}
