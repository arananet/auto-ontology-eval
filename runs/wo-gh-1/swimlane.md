# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (8 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 3218.469 | runs/wo-gh-1/intake.output.md | null |
| spec-writer | executed | 37579.142 | runs/wo-gh-1/spec-writer.output.md | null |
| test-writer | executed | 166290.557 | runs/wo-gh-1/test-writer.output.md | null |
| builder | failed | 1500178.448 | runs/wo-gh-1/builder.packet.md | null |
| checks-gate | not_configured | 6.237 | runs/wo-gh-1/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 31124.578 | runs/wo-gh-1/reviewer-spec.output.md | null |
| reviewer-security | executed | 29047.712 | runs/wo-gh-1/reviewer-security.output.md | null |
| reviewer-tests | executed | 43897.251 | runs/wo-gh-1/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 17578.335 | runs/wo-gh-1/reviewer-architecture.output.md | null |
| reviewer-design | failed | 15436.282 | runs/wo-gh-1/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 0.604 | runs/wo-gh-1/reviewer-ux.packet.md | null |
| approver | completed | 0.023 | runs/wo-gh-1/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.005 | - | null |
| deployer | packet_ready | 0.159 | runs/wo-gh-1/deployer.packet.md | null |
| observer | executed | 35355.574 | runs/wo-gh-1/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-tests requested changes. (Counted 1 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
