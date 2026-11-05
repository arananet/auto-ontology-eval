# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (9 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 3370.393 | runs/wo-gh-1/intake.output.md | null |
| spec-writer | executed | 38848.96 | runs/wo-gh-1/spec-writer.output.md | null |
| test-writer | executed | 331818.281 | runs/wo-gh-1/test-writer.output.md | null |
| builder | executed | 449494.87 | runs/wo-gh-1/builder.output.md | null |
| checks-gate | not_configured | 0.079 | runs/wo-gh-1/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 21275.635 | runs/wo-gh-1/reviewer-spec.output.md | null |
| reviewer-security | executed | 44719.308 | runs/wo-gh-1/reviewer-security.output.md | null |
| reviewer-tests | executed | 20648.392 | runs/wo-gh-1/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 22083.339 | runs/wo-gh-1/reviewer-architecture.output.md | null |
| reviewer-design | failed | 13983.216 | runs/wo-gh-1/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 0.906 | runs/wo-gh-1/reviewer-ux.packet.md | null |
| approver | completed | 0.04 | runs/wo-gh-1/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.008 | - | null |
| deployer | packet_ready | 0.226 | runs/wo-gh-1/deployer.packet.md | null |
| observer | executed | 44696.548 | runs/wo-gh-1/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-architecture requested changes. (Counted 2 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
