I made two small changes to the spec. Neither one adds a new scenario or changes S1–S3.

**Where the spec is:** `/home/runner/work/auto-ontology-eval/auto-ontology-eval/.openspec/specs/auto-ontology-enterprise-eval/spec.md`. That's the project repo's root, not `.anvil-factory/`. It already had scenarios S1–S5 and three amendments, and S1–S3 already match the rescoped work order.

**What changed:**
1. **Key rule now covers uploaded artifacts.** The old rule kept `NVIDIA_API_KEY` out of code, committed files, logs and RESULTS.md. The rescoped work order also says "never written to … artifacts", and the workflow uploads the run directory with `actions/upload-artifact`. So the rule now names run artifacts too, whether committed or uploaded. It also says any file that has to carry the key, like the Compose env file, must be written outside the run evidence directory. I checked the current code and it already does this: `_env_file` in `src/auto_ontology_eval/live.py` writes the key to the upstream checkout under `RUNNER_TEMP`, not to the run directory.
2. **New "Work order coverage" section, for reference only.** It notes that wo-gh-1 as rescoped covers S1–S3 and the requirements that apply to them. S4, S5 and Amendment 3 stay in the spec unchanged for a follow-up work order.

**Model name conflict:** the rescoped work order still names the chat model `nvidia/nemotron-3-nano-30b-a3b`. The spec's Amendment 2 replaces it with `nvidia/nemotron-3.5-lightning-30b-a3b`, because the original model returned HTTP 410 (retired) and the first replacement returned HTTP 404 on this account. The new section records that the amendment wins. The embedding and reranking models in the work order match the spec.

**Left for others:**
- The spec header still says `Status: draft`. Changing that is for the approver station or the spec owner.
- I didn't add any amendment in the owner's name. Writing amendments is their decision.
- This station doesn't approve its own work, so the change still needs review.

**Nothing is missing:** the work order and the brain had everything I needed for this revision.
{"model": "claude-opus-5-5"}
