I revised the spec in place: `/home/runner/work/auto-ontology-eval/auto-ontology-eval/.openspec/specs/auto-ontology-enterprise-eval/spec.md`. It lives in the project repo, not the `.anvil-factory` checkout, because that's where the work order's spec path and the run's `runs/wo-gh-1/` folder are. The spec already covered S1 to S5 and matched the work order, so I kept the scope and wording and only closed gaps that a reviewer or QA station would otherwise have to guess at.

What changed:
- **Secrets requirement:** if `NVIDIA_API_KEY` is missing or empty, the run stops before S1. It never falls back to another key, another model or placeholder results. This covers the `secrets` risk hint, and `OPERATOR-NOTES.md` says the secret doesn't exist on the repo yet.
- **New requirement on model settings:** both S4 arms must use the same chat model id, endpoint and temperature, and the run saves those settings as an artifact. This makes the comparison between the two arms fair.
- **S2:** the fixture must include a machine-readable checklist of at least four planted conflicts: the `net_sales` definition, the product hierarchy, location names versus plant and DC codes (with the true mapping recorded), and SKU identity across the two sources.
- **S3:** the harness checks mechanically that each evidence quote appears word for word in the exported catalog. If a quote fails that check, the conflict is reported as ignored.
- **S4:** "Exact-answer correctness" now uses a normalization rule written down before any model runs. At least one question must test each planted conflict. A chat API error or an answer with no SQL counts as wrong, and the harness doesn't retry it until it passes.

Two things for later stations:
- **Approval:** the work order calls the spec "approved", but its header still says `Status: draft`. I left it as draft because this station can't approve its own work, so a different station has to approve it.
- **Not committed:** nothing is committed. The `line-output.log` change and the untracked `runs/` and `work_orders/` folders in the working tree are not mine.
{"model": "claude-opus-5-5"}
