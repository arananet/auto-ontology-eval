I wrote the observation report to `runs/wo-gh-1/observer.output.md`, and it says there was no release to observe. I staged the file but didn't commit it.

The report is in the project root, not the `.anvil-factory` directory. That directory holds an older run of an unrelated work order that is also called `wo-gh-1`.

- **No release record:** The deployer only wrote a packet (`packet_ready`), and `report.json` shows `deployment_status: null`. I didn't infer a release.
- **Preflight failed:** The run stopped at preflight because the old chat model `nvidia/nemotron-3-nano-30b-a3b` returned HTTP 410. That model reached end of life on 2026-09-01. The embedding and rerank models returned 200.
- **No evidence for S1, S3 or S4:** S1 smoke, time to first ontology, the reconciliation checklist and the ablation never ran. There is no top-level `RESULTS.md`, only a stub inside the preflight evidence folder. The S2 fixture exists in the repo but was never run against the stack.
- **Spec amendment not yet exercised:** Spec Amendment 1 replaces the chat pin, but the preflight run used the old one.
- **Approver verdict:** The approver verdict is `changes_requested`. The reviewer-architecture review requested changes and only 2 of 5 expected reviews were counted. The reviewer-design station failed with empty output. The loopback is about `NVIDIA_API_KEY` being read only from the repository secret.

The report recommends fixing the loopback items and re-running with the amended pin. It also says no claim about Auto Ontology should be made from this run.
{"model": "claude-sonnet-5-5"}
