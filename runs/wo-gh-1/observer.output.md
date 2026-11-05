I wrote the observation report to `runs/wo-gh-1/observer.output.md` in the project root. It says nothing was released and the evaluation produced no results.

- **Release:** the release record is only a packet (`packet_ready`). No release step ran.
- **Run:** the one real run (GitHub run `41971180197`) stopped at the model preflight. The chat model `nvidia/nemotron-3-nano-30b-a3b` returned HTTP 410 because it reached end of life on 2026-09-01. The embedding and rerank models returned 200.
- **Evidence:** S1, S3, S4 and S5 have no run evidence. The fixture (S2) was built and tested offline only. I make no claim about Auto Ontology itself.
- **Process:**
  - The run's verdict is `changes_requested`, with only 3 of 5 reviews counted.
  - `reviewer-design` failed because codex produced empty output.
  - The packet went on to triage-human and the deployer anyway, and I couldn't tell why from the inputs. A human should look at that.
- **Next step:** the spec owner has to pin a replacement chat model in the spec, because the spec forbids the harness switching models itself. The report lists the candidates from the builder's preflight note.

The tracked `runs/wo-gh-1/observer.output.md` was already in git, and git shows it as modified. I overwrote it, so use `git diff` there if you need what was in it before.

I worked in the project root (`/home/runner/work/auto-ontology-eval/auto-ontology-eval`), not the `.anvil-factory` directory. That directory holds an old `runs/wo-gh-1` from an unrelated design-system work order with the same id.
{"model": "claude-sonnet-5-5"}
