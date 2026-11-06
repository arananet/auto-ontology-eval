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
- description: Implement spec auto-ontology-enterprise-eval (S1–S3 only) in the factory: (S1) stand up NVIDIA/auto-ontology at pinned commit cdaf61e1bd0cf3820d11d72b43bb460816aebbd3 via its own Docker Compose on a Docker-capable GitHub Actions runner and record smoke evidence (API health check, one catalog page or API response, an MCP tools/list or equivalent probe); (S2) build the deterministic two-source fixture with planted conflicts (Source A Postgres sales mart where net_sales excludes returns and hierarchy is brand then category; Source B DuckDB ops mart where net_sales is gross including returns and locations use plant/DC codes differing from Source A names; shared SKUs; 8 to 10 tables total; fixed seeds; ground truths documented inside the fixture); (S3) run ontology generation against both sources with the default hosted NIM configuration (chat nvidia/nemotron-3-nano-30b-a3b, embeddings nvidia/nemotron-3-embed-1b, rerank nvidia/llama-nemotron-rerank-vl-1b-v2), with the API key supplied only as the NVIDIA_API_KEY repository secret (never written to logs, artifacts, or the repo), and score the generated ontology against the planted-conflict checklist, marking each conflict detected, reconciled, or ignored, each mark backed by a verbatim quote from the generated catalog. No real company data is used and nothing is published.
- risk_hints: secrets
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: not_configured

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-1/reviewer-spec.review.json. The free output transcript stays as provenance and is never parsed for a review.
