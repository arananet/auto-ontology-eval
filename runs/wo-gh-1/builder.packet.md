# Task packet: builder

## Station prompt

# Builder

## Role
Implement the spec so the scenario tests pass.

## Inputs
- spec
- tests

## Outputs
- code change

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.
- **Design citation**: When authoring or revising design/DESIGN.md, include a "Design knowledge sources" note citing the knowledge entries you drew from by data kind and entry name (e.g., "Style: modern-minimal", "Palette: metrics-blue", "Guideline: accessibility - contrast ratio"). If the knowledge came from an operator-supplied pack, cite it as "operator-supplied pack entry" without naming the pack's origin.

### Visual Output Quality Verification

When your packet includes a Quality Charter section (visual runs only), you must verify each produced output against the run's reference anchors and charter criteria before the review step:

1. **Read the output**: Examine each visual deliverable you produce (images, UI components, rendered interfaces).

2. **Compare against anchors**: If reference anchors are provided, compare your output against them. Check how your output measures up to the anchor's quality bar across the charter criteria.

3. **Check charter criteria**: Evaluate your output against the observable criteria from the Quality Charter:
   - For physical products: materials, light, contact, scale
   - For games/illustrations: the stated standard from the project design system

4. **Record the comparison**: Document your findings in the run evidence directory (runs/{work_order_id}/evidence/) as a JSON file named `{output_filename}.comparison.json` with this structure:

```json
{
  "output": "path/to/generated/output.png",
  "anchor_cited": "path/to/reference/anchor.png or null if none",
  "criteria_checked": ["materials", "light", "contact", "scale"],
  "gaps": [
    {
      "criterion": "materials",
      "description": "Surfaces read as plastic rather than the metal shown in anchor"
    }
  ],
  "statement": "Explicit statement: 'No gaps found at charter bar' or description of gaps identified"
}
```

5. **Evidence, not verdict**: Your comparison is evidence for reviewers, not a final verdict. Record what you observe; reviewers are not bound by your self-assessment.

This verification step only applies when the Quality Charter section is present in your packet. For non-visual work, this step does not apply.


## Design knowledge

**Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The knowledge base below is reference material that the design system may draw from. On any conflict, the project's design system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.

**Note**: No product type slice matched. General guidelines only.

### Product Type: Undeclared

No specific product type declared. Using general guidelines only.

### UX Guidelines

**Accessibility:**
- Maintain minimum 4.5:1 contrast ratio for normal text, 3:1 for large text (18pt+)
- Touch targets must be at least 44x44px on mobile devices

**Feedback:**
- Loading states should appear after 300ms delay to avoid flashing
- Provide immediate visual feedback for user actions

**Forms:**
- Form fields should have clear labels and validation feedback
- Error messages should explain what went wrong and how to fix it

**Hierarchy:**
- Establish clear visual hierarchy using size, weight, and color
- Important actions should be visually prominent and easy to locate

**Motion:**
- Keep animation durations between 200-400ms for most transitions
- Provide reduced motion alternatives for users with vestibular sensitivity

**Responsive:**
- Test layouts at mobile (320-768px), tablet (768-1024px), and desktop (1024px+) breakpoints
- Avoid horizontal scrolling on standard viewports

**Spacing:**
- Use consistent spacing scale throughout (e.g., 4px, 8px, 16px, 24px, 32px)
- Group related elements together with whitespace separating distinct sections


## Quality Charter

Product type: physical_product

Observable criteria:

- **Materials**: Surfaces read as the materials the product is actually made of
- **Light**: One coherent light story, with shadows and reflections that agree with it
- **Contact**: Objects meet skin, surfaces and each other the way physical things do
- **Scale**: The object's size reads true against its context and human anatomy


## Reference Anchors

⚠️ **WARNING**: This run has no reference anchors.

The review will proceed under the charter floor alone.


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
