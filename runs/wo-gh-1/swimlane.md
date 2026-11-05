# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 3616.163 | runs/wo-gh-1/intake.output.md | null |
| spec-writer | executed | 28708.015 | runs/wo-gh-1/spec-writer.output.md | null |
| test-writer | executed | 262082.185 | runs/wo-gh-1/test-writer.output.md | null |
| builder | executed | 145148.921 | runs/wo-gh-1/builder.output.md | null |
| checks-gate | not_configured | 0.063 | runs/wo-gh-1/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 33141.157 | runs/wo-gh-1/reviewer-spec.output.md | null |
| reviewer-security | executed | 40734.966 | runs/wo-gh-1/reviewer-security.output.md | null |
| reviewer-tests | executed | 32434.309 | runs/wo-gh-1/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 22404.961 | runs/wo-gh-1/reviewer-architecture.output.md | null |
| reviewer-design | executed | 14591.803 | runs/wo-gh-1/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 0.807 | runs/wo-gh-1/reviewer-ux.packet.md | null |
| approver | completed | 0.034 | runs/wo-gh-1/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.255 | runs/wo-gh-1/deployer.packet.md | null |
| observer | executed | 72395.457 | runs/wo-gh-1/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-design requested changes. (Counted 3 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
