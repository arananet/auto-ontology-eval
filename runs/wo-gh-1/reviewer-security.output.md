I wrote the review to `runs/wo-gh-1/reviewer-security.review.json` with verdict `pass`. The file parses as valid JSON. I read the code but did not run the workflow.

- **Secret handling:** `NVIDIA_API_KEY` comes only from the repository secret. The harness fails closed if it is missing, with no fallback key or model. The key is written only to a 0600 `.env` file, which teardown deletes. Every artifact write path redacts the key and anything shaped like an `nvapi-` key.
- **Workflow:** it runs on `workflow_dispatch` only, so fork PRs can't reach the secret. Permissions are `contents: read`, nothing is published, and subprocesses use argument lists rather than a shell. The upstream clone is checked against the pinned commit.
- **Advisory, not blocking:**
  - The three GitHub Actions are pinned by tag, not by commit SHA.
  - The upstream stack may publish ports on the runner, which is fine on an ephemeral runner.
  - The `.env` sits in the upstream build context, so an upstream `COPY .` could bake the key into the local image. The image is never pushed, so the risk is low.
- **Scope note:** the review covers the real code in the parent checkout, not the `builder.output.md` in the run directory. That file describes an unrelated design-system feature, which `reviewer-spec` already flagged.
{"model": "claude-sonnet-5-5"}
