# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (9 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 3847.675 | runs/wo-gh-1/intake.output.md | null |
| spec-writer | executed | 47506.369 | runs/wo-gh-1/spec-writer.output.md | null |
| test-writer | executed | 279350.06 | runs/wo-gh-1/test-writer.output.md | null |
| builder | executed | 684161.328 | runs/wo-gh-1/builder.output.md | null |
| checks-gate | not_configured | 0.07 | runs/wo-gh-1/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 119395.931 | runs/wo-gh-1/reviewer-spec.output.md | null |
| reviewer-security | executed | 49176.545 | runs/wo-gh-1/reviewer-security.output.md | null |
| reviewer-tests | executed | 46118.571 | runs/wo-gh-1/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 18508.666 | runs/wo-gh-1/reviewer-architecture.output.md | null |
| reviewer-design | failed | 12937.374 | runs/wo-gh-1/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 0.755 | runs/wo-gh-1/reviewer-ux.packet.md | null |
| approver | completed | 0.039 | runs/wo-gh-1/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.096 | runs/wo-gh-1/deployer.packet.md | null |
| observer | executed | 34364.821 | runs/wo-gh-1/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-tests requested changes. (Counted 3 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
