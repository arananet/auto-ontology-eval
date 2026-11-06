# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 6147.198 | runs/wo-gh-1/intake.output.md | null |
| spec-writer | executed | 41591.434 | runs/wo-gh-1/spec-writer.output.md | null |
| test-writer | executed | 101631.335 | runs/wo-gh-1/test-writer.output.md | null |
| builder | executed | 49744.214 | runs/wo-gh-1/builder.output.md | null |
| checks-gate | not_configured | 0.092 | runs/wo-gh-1/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 41873.522 | runs/wo-gh-1/reviewer-spec.output.md | null |
| reviewer-security | executed | 44870.912 | runs/wo-gh-1/reviewer-security.output.md | null |
| reviewer-tests | executed | 25889.346 | runs/wo-gh-1/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 22395.366 | runs/wo-gh-1/reviewer-architecture.output.md | null |
| reviewer-design | executed | 11533.43 | runs/wo-gh-1/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 0.804 | runs/wo-gh-1/reviewer-ux.packet.md | null |
| approver | completed | 0.039 | runs/wo-gh-1/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.185 | runs/wo-gh-1/deployer.packet.md | null |
| observer | executed | 37087.325 | runs/wo-gh-1/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-design requested changes. (Counted 3 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
