# Task packet: reviewer-design

## Station prompt

# Reviewer Design

## Role
Judge interface output against the project's own design system: its design tokens, component and layout rules, motion rules, and quality bars.

## Inputs
- design system (tokens, rules, quality bars from design/DESIGN.md and design/tokens.json)
- interface output (HTML, React components, CSS, user-facing pages, or other interface artifacts)

## Outputs
- review (JSON format with verdict and findings)

## Rules
- Work only from the inputs listed above and the work order in the packet.
- If the project has no design system (no design/DESIGN.md), your verdict MUST be `changes_requested` with a finding stating that no design system exists for the project.
- If the project has a design system, review the interface output against:
  - Design tokens: Are the correct colors, typography, spacing values being used?
  - Component and layout rules: Do components follow the documented patterns?
  - Motion rules: Does any animation or transition follow the motion guidelines?
  - Quality bars: Does the interface meet the stated quality bars for visual hierarchy, scale contrast, spacing rhythm, and responsive behavior?
- **Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The Design knowledge section in your packet (when present) is reference material that the design system may draw from. On any conflict between the project's design system and the knowledge base, the project's design system wins. A deviation from the knowledge base alone is never a finding; a deviation from the project's design system is.
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed. When referencing the Design knowledge base in a finding or suggestion, name the specific knowledge entry (e.g., "metrics-blue palette", "data-dense style", "accessibility guideline for contrast").
- Your verdict must be one of: `pass`, `fail`, or `changes_requested`.
- Produce the output as a JSON object, not as chat text.

## Output Format

For visual runs (when Quality Charter is present in your packet), return a JSON object with dual-section structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "compliance": {
    "verdict": "pass | fail | changes_requested",
    "findings": [
      "Design system compliance findings (tokens, rules, component patterns)"
    ]
  },
  "quality": {
    "verdict": "pass | fail | changes_requested",
    "findings": [
      "Quality findings comparing output against reference anchors and charter criteria"
    ],
    "anchor": "path/to/anchor/file or 'charter floor only' when no anchors"
  }
}

For non-visual runs (no Quality Charter in packet), return the simple structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar"
  ]
}

### Dual-Section Review (Visual Runs)

For visual runs:

1. **Compliance section**: Judge design system adherence - tokens, component patterns, layout rules, motion guidelines.

2. **Quality section**: Judge visual quality by comparing the output against reference anchors and charter criteria. This is a separate judgment from compliance.
   - When reference anchors are present: Compare the output against the anchors. Name gap categories from the charter criteria (materials, light, scale, contact for physical products; stated criteria for games/illustrations).
   - When no anchors: Judge against charter floor alone.
   - Cite the anchor used in comparison or state "charter floor only" when no anchors available.

The overall verdict is the stricter of the two section verdicts. An output can pass compliance but fail quality, and such a case must be reported as changes_requested or fail at the overall level.

**Same-Subject Identity Consistency (S7)**: When the work order declares an `identity_reference` for runs producing multiple related visual outputs, the quality section may extend beyond individual anchor evaluation to include same-subject identity consistency verification across deliverable outputs. Your packet will specify this requirement when applicable. You must verify that all outputs maintain identical subject identity traits enumerated in the work order (examples for physical products: finish, detail colors, mounting or attachment, proportions and markings; stated equivalents apply for other product types). Divergence in these traits constitutes a quality failure even when each output individually meets anchor criteria. Such failures must name the specific output and trait in your findings, with ruling and evidence recorded in the quality section. This verification is part of quality section judgment, not a separate verdict.

### Quality Criteria by Product Type

When judging quality section findings, name specific criteria gaps:

**Physical products**: materials, light, contact, scale
**Games/Illustrations**: Apply the project's stated standard from the design system

The station field must equal "reviewer-design", and both the overall verdict and section verdicts must be one of pass, fail, or changes_requested.

## Examples

Example 1: No design system exists
- verdict: changes_requested
- finding: "No design system exists for this project. The project must define design/DESIGN.md and design/tokens.json before interface output can be reviewed against design standards."

Example 2: Interface violates quality bar
- verdict: changes_requested
- findings:
  * "Quality bar violation: Scale Contrast - The button text has only 2.8:1 contrast ratio against its background, failing the minimum 4.5:1 requirement stated in the quality bars."
  * "Token usage: The page uses hardcoded color '#FF5733' instead of the defined primary color token."

Example 3: Interface meets design system
- verdict: pass
- findings: (empty list)


<!-- source: design/DESIGN.md -->


## Spec



## Diff summary

- .openspec/specs/auto-ontology-enterprise-eval/spec.md: +5, -3
- line-output.log: +0, -1
- runs/wo-gh-1/builder.output.md: +28, -17
- runs/wo-gh-1/envelopes/builder.envelope.json: +1, -1
- runs/wo-gh-1/envelopes/checks-gate.envelope.json: +1, -1
- runs/wo-gh-1/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-1/envelopes/reviewer-architecture.envelope.json: +14, -2
- runs/wo-gh-1/envelopes/reviewer-security.envelope.json: +7, -8
- runs/wo-gh-1/envelopes/reviewer-spec.envelope.json: +2, -16
- runs/wo-gh-1/envelopes/reviewer-tests.envelope.json: +2, -14
- runs/wo-gh-1/envelopes/spec-writer.envelope.json: +1, -1
- runs/wo-gh-1/envelopes/test-writer.envelope.json: +1, -1
- runs/wo-gh-1/intake.output.md: +1, -7
- runs/wo-gh-1/reviewer-architecture.output.md: +7, -6
- runs/wo-gh-1/reviewer-security.output.md: +10, -8
- runs/wo-gh-1/reviewer-security.review.json: +6, -7
- runs/wo-gh-1/reviewer-spec.output.md: +11, -6
- runs/wo-gh-1/reviewer-spec.review.json: +0, -15
- runs/wo-gh-1/reviewer-tests.output.md: +8, -6
- runs/wo-gh-1/reviewer-tests.review.json: +0, -13
- runs/wo-gh-1/routing.json: +2, -2
- runs/wo-gh-1/spec-writer.output.md: +11, -10
- runs/wo-gh-1/test-writer.output.md: +30, -17

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/auto-ontology-enterprise-eval/spec.md
- line-output.log
- runs/wo-gh-1/builder.output.md
- runs/wo-gh-1/envelopes/builder.envelope.json
- runs/wo-gh-1/envelopes/checks-gate.envelope.json
- runs/wo-gh-1/envelopes/intake.envelope.json
- runs/wo-gh-1/envelopes/reviewer-architecture.envelope.json
- runs/wo-gh-1/envelopes/reviewer-security.envelope.json
- runs/wo-gh-1/envelopes/reviewer-spec.envelope.json
- runs/wo-gh-1/envelopes/reviewer-tests.envelope.json
- runs/wo-gh-1/envelopes/spec-writer.envelope.json
- runs/wo-gh-1/envelopes/test-writer.envelope.json
- runs/wo-gh-1/intake.output.md
- runs/wo-gh-1/reviewer-architecture.output.md
- runs/wo-gh-1/reviewer-security.output.md
- runs/wo-gh-1/reviewer-security.review.json
- runs/wo-gh-1/reviewer-spec.output.md
- runs/wo-gh-1/reviewer-spec.review.json
- runs/wo-gh-1/reviewer-tests.output.md
- runs/wo-gh-1/reviewer-tests.review.json
- runs/wo-gh-1/routing.json
- runs/wo-gh-1/spec-writer.output.md
- runs/wo-gh-1/test-writer.output.md

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

## Rendered evidence

**Note:** Rendered evidence could not be captured for this run. Reason: no servable configuration found. This review judged source only.


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

