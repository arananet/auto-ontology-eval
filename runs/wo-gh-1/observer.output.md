I wrote the observation report to `runs/wo-gh-1/observer.output.md` in the project repo, the parent of `.anvil-factory`. I didn't commit it, and I didn't rerun anything. The `.anvil-factory/runs/wo-gh-1/` directory holds an unrelated work order that reuses the id `wo-gh-1`, so I ignored it.

- **Release record:** the deployer only produced a packet (`packet_ready`). Nothing was released or published, which fits the work order. The record is not an approved change: the builder and reviewer-design steps failed, and the approver step ended in a loopback.
- **Executed run:** the harness ran end to end (GitHub run 42127124473). The Auto Ontology arm scored 0/12 and the raw-schema arm 8/12, a delta of -8. All 4 planted conflicts were marked `ignored`.
- **Why the numbers mean little:** the diagnosis file says the product's internal models were still set to the retired `nvidia/nemotron-3-nano-30b-a3b`. Every internal LLM call returned HTTP 410. So the run shows the product with its LLM steps disabled, not what it can do.
- **No evidence for Amendment 3:** the config fix landed after the run, and no run uses it.
- **Other deviations:**
  - The run used `nvidia/nemotron-3.5-lightning-30b-a3b`, not the model in the spec.
  - The raw-schema arm ran on SQLite, not on the live sources.
  - The MCP check was in-process rather than over the network.
- **Working tree:** it has uncommitted changes, including a deleted `builder.output.md`, so the release record I read may differ from the committed one.

The report recommends rerunning the evaluation under Amendment 3 and resolving the failed steps before release. I didn't approve anything.
{"model": "claude-sonnet-5-5"}
