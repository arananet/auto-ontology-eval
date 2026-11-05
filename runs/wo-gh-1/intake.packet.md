# Task packet: intake

## Station prompt

# Intake Station

## Role

Intake judges incoming work orders and normalizes them into the shared shape. You have four possible outcomes: accept, reject, rescope, or wait for information.

## Outcomes

### Accepted

The work order is buildable as stated. Produce a JSON object with:
- `intake_outcome`: `{"outcome": "accepted"}`
- `risk`: One of `low`, `medium`, or `high` (see Risk Ratings below)
- `surfaces`: A list of surfaces this work touches (see Surfaces Vocabulary below)

### Rejected

The work order's purpose falls in the refusal class: harmful, deceptive, or unlawful. Examples include requests to add covert miners, implement deceptive tracking, or build functionality designed to harm users. Never quietly reformulate refused work into something buildable.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rejected", "reasons": ["reason 1", "reason 2", ...]}`

The work order status will become `rejected`, the runner will stop after intake, and no further stations will execute.

### Rescoped

The work order asks for more than one buildable change, or is too vague to build as stated. Cut it down to one buildable scope and record what was removed and why.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rescoped", "rescoped_description": "The buildable scope", "reasons": ["what was cut and why"]}`
- `risk`: Risk rating for the rescoped work
- `surfaces`: Surfaces the rescoped work touches

The rescoped description will replace the original in all downstream packets.

### Waiting for Information

The work order lacks information you need to judge it. Record your questions.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "waiting_info", "questions": ["question 1", "question 2", ...]}`

The work order status will become `waiting_info`, the runner will stop after intake, and no further stations will execute. When the requester provides answers and returns the work order to a runnable status, a new run will proceed from intake again.

## Risk Ratings

- **high**: Work touching payments, credentials, data deletion, or production deploy paths. High blast radius or irreversible changes.
- **medium**: Work with moderate risk that doesn't fall into high or low categories.
- **low**: Small, reversible changes with limited blast radius.

## Surfaces Vocabulary

Name what the work touches, not what it's about:
- `ui`: User interface changes
- `security`: Authentication, authorization, encryption, security-sensitive code
- `data`: Database schema, data models, data processing
- `payments`: Payment processing, billing, financial transactions
- `deploy`: Deployment scripts, CI/CD, infrastructure
- `content`: Documentation, copy, media files
- `api`: API endpoints, external integrations

Use the surfaces that apply. One work order can touch multiple surfaces.

## Output Format

Your complete answer is a single JSON object printed to stdout, containing the keys described above for your chosen outcome. The runner parses this JSON to determine how to proceed.


## Work order

- id: wo-gh-1
- kind: feature
- title: Evaluate NVIDIA Auto Ontology as an enterprise semantic layer (executed ablation test)
- source: github-issue
- description: Spec: .openspec/specs/auto-ontology-enterprise-eval/spec.md (slug auto-ontology-enterprise-eval), approved and written before this implementation. Implement it in the factory.

The problem it solves: NVIDIA Auto Ontology claims it can generate a semantic layer over enterprise data, reconcile conflicting definitions across systems, and serve that layer to agents through MCP. Those claims are currently vendor claims. This work order replaces them with executed evidence on a fixture designed to stress exactly the reconciliation claim, before any writing about the tool is considered.

What to build, per the spec scenarios:

S1: Stand up NVIDIA/auto-ontology at the pinned commit cdaf61e1bd0cf3820d11d72b43bb460816aebbd3 with its own Docker Compose on a Docker-capable GitHub Actions runner. Record smoke evidence: API health check, one catalog page or API response, and an MCP tools/list or equivalent probe.

S2: Build a deterministic two-source fixture with planted conflicts: Source A, a Postgres sales mart where net_sales excludes returns and the product hierarchy is brand then category; Source B, a DuckDB ops mart where net_sales is gross including returns and locations use plant and DC codes that differ from Source A names for the same entities; shared SKUs across both. 8 to 10 tables total, fixed seeds, ground truths documented inside the fixture.

S3: Run ontology generation against both sources with the default hosted NIM configuration (chat nvidia/nemotron-3-nano-30b-a3b, embeddings nvidia/nemotron-3-embed-1b, rerank nvidia/llama-nemotron-rerank-vl-1b-v2), the API key supplied only as the NVIDIA_API_KEY repository secret. Score the generated ontology against the planted-conflict checklist: every conflict marked detected, reconciled or ignored, each mark backed by a verbatim quote from the generated catalog.

S4: Ablation over 12 natural-language questions with ground truths computed by reference SQL: each question answered through the Auto Ontology chat API and by the same LLM with raw schema only. Score exact-answer correctness per arm, record the delta, and record whether each Auto Ontology answer carries provenance or lineage.

S5: Produce RESULTS.md from the executed run only: environment, pinned commit, model ids, time to first ontology, the reconciliation checklist, the per-question table for both arms, a failure gallery with verbatim wrong SQL, and a limits section. No claim in RESULTS.md may exceed what the fixture exercised.

No real company data is used, and nothing is published from this work order.
- risk_hints: secrets
- status: new

## Upstream steps

- (none)
