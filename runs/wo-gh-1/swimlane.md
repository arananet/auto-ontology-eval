# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (9 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 3970.248 | runs/wo-gh-1/intake.output.md | null |
| spec-writer | executed | 35353.792 | runs/wo-gh-1/spec-writer.output.md | null |
| test-writer | executed | 103496.057 | runs/wo-gh-1/test-writer.output.md | null |
| builder | executed | 94367.558 | runs/wo-gh-1/builder.output.md | null |
| checks-gate | not_configured | 0.08 | runs/wo-gh-1/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 197089.916 | runs/wo-gh-1/reviewer-spec.output.md | null |
| reviewer-security | executed | 30244.703 | runs/wo-gh-1/reviewer-security.output.md | null |
| reviewer-tests | executed | 19487.582 | runs/wo-gh-1/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 22547.568 | runs/wo-gh-1/reviewer-architecture.output.md | null |
| reviewer-design | failed | 16798.336 | runs/wo-gh-1/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 0.926 | runs/wo-gh-1/reviewer-ux.packet.md | null |
| approver | completed | 0.048 | runs/wo-gh-1/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.236 | runs/wo-gh-1/deployer.packet.md | null |
| observer | executed | 33470.751 | runs/wo-gh-1/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-spec requested changes. (Counted 1 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
