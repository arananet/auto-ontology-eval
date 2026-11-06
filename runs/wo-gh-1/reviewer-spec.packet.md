# Task packet: reviewer-spec

## Station prompt

# Reviewer Spec

## Role
Check the implementation against the spec, nothing else.

## Inputs
- spec
- code change

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-spec",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-spec", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


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

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: failed
- checks-gate: not_configured

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-1/reviewer-spec.review.json. The free output transcript stays as provenance and is never parsed for a review.
