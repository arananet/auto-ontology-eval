# auto-ontology-eval

![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue) ![Docker Compose](https://img.shields.io/badge/docker-compose-blue) ![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green) ![OpenSpec](https://img.shields.io/badge/OpenSpec-specs-orange)

> "An executed evaluation of NVIDIA Auto Ontology as an enterprise semantic layer: planted conflicts, an ablation test, and results that claim only what the run exercised."

## What it is

This project evaluates NVIDIA Auto Ontology as a candidate enterprise semantic layer. Auto Ontology claims it can generate an ontology from the metadata of connected data sources, reconcile conflicting definitions across systems, and serve that layer to agents through MCP, a CLI and an API. Those claims are tested here with an executed run, not repeated from vendor material.

It is an ANVIL factory project: the evaluation was specified before any implementation, and the harness is built and executed by the factory line on GitHub Actions.

## The evaluation

The spec under `.openspec/specs/auto-ontology-enterprise-eval/` defines five scenarios:

- S1: Stand up NVIDIA/auto-ontology at a pinned commit with its own Docker Compose on a Docker-capable runner, and record smoke evidence (API health, a catalog response, an MCP probe).
- S2: Build a deterministic two-source fixture with planted conflicts: a Postgres sales mart where net_sales excludes returns and the product hierarchy is brand then category, and a DuckDB ops mart where net_sales includes returns and locations use plant and DC codes that differ from the sales mart names for the same entities. Shared SKUs across both, 8 to 10 tables, ground truths documented in the fixture.
- S3: Generate the ontology against both sources with the default hosted NIM models and score it against the planted-conflict checklist, every mark backed by a verbatim quote from the generated catalog.
- S4: Ablation: 12 natural-language questions with ground truths from reference SQL, answered through the Auto Ontology chat API and by the same LLM with raw schema only. Correctness is scored per arm and the delta recorded, along with whether each ontology answer carries provenance.
- S5: RESULTS.md written from the executed run only: environment, pinned commit, model ids, time to first ontology, the reconciliation checklist, the per-question table, a failure gallery with verbatim wrong SQL, and a limits section.

No real company data is used anywhere in this project. The evaluation and its diagnosis are written up in a LinkedIn article: https://www.linkedin.com/pulse/i-planted-four-conflicts-database-asked-nvidia-auto-ontology-arana-axswe/

## Status

Executed. The default-configuration run completed on GitHub Actions on 2026-11-05 (run 42127124473) at the pinned upstream commit, with the evaluation chat model pinned by recorded spec amendment to nvidia/nemotron-3.5-lightning-30b-a3b. Headline results: first complete catalog in 15.42 s; all four planted conflicts scored ignored; the Auto Ontology chat arm answered 0 of 12 questions against 8 of 12 for the raw-schema control. The full evidence is on the `anvil/run-auto-ontology-eval` branch: [RESULTS.md](https://github.com/arananet/auto-ontology-eval/blob/anvil/run-auto-ontology-eval/runs/eval/RESULTS.md) and the [diagnosis of the chat arm's silence](https://github.com/arananet/auto-ontology-eval/blob/anvil/run-auto-ontology-eval/runs/eval/S4-DIAGNOSIS.md). A second run with the product's internal models wired to the live pinned model (spec Amendment 3) is in progress; its results will land in `runs/eval-live/` on the same branch.

## Repository layout

- `.openspec/specs/`: the evaluation spec, written before implementation
- `work-orders/`: the work order the factory line executes
- `brain/`: project context, principles and decisions
- `runs/`: run evidence committed by the line after an executed run

## Contributing

Every change starts with a spec under .openspec/specs/ (OpenSpec). Write the spec, write tests that map to its scenarios, then implement. Work enters through a work order; see CONTRIBUTING.md.

## Documentation

| Document | What it covers |
|---|---|
| [.openspec/specs/auto-ontology-enterprise-eval/spec.md](.openspec/specs/auto-ontology-enterprise-eval/spec.md) | The evaluation contract: purpose, requirements and scenarios S1 to S5 |
| [OPERATOR-NOTES.md](OPERATOR-NOTES.md) | Pinned upstream commit, execution blockers and the exact step that fires the run |
| [PIPELINES.md](PIPELINES.md) | The ANVIL pipeline this project runs on |

## License

[Apache 2.0](LICENSE)

---

## Developer

Eduardo Arana

## Support this with a ko-fi

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/H2H51MPWG)
