# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (9 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 3885.637 | runs/wo-gh-1/intake.output.md | null |
| spec-writer | executed | 54137.31 | runs/wo-gh-1/spec-writer.output.md | null |
| test-writer | executed | 64326.227 | runs/wo-gh-1/test-writer.output.md | null |
| builder | executed | 59939.851 | runs/wo-gh-1/builder.output.md | null |
| checks-gate | not_configured | 10.557 | runs/wo-gh-1/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 40204.605 | runs/wo-gh-1/reviewer-spec.output.md | null |
| reviewer-security | executed | 55241.647 | runs/wo-gh-1/reviewer-security.output.md | null |
| reviewer-tests | executed | 25626.844 | runs/wo-gh-1/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 22173.021 | runs/wo-gh-1/reviewer-architecture.output.md | null |
| reviewer-design | failed | 24232.711 | runs/wo-gh-1/reviewer-design.packet.md | null |
| reviewer-ux | routed_out | 0.889 | runs/wo-gh-1/reviewer-ux.packet.md | null |
| approver | completed | 0.082 | runs/wo-gh-1/report.json | null |
| triage-human | completed | 0.017 | - | null |
| deployer | packet_ready | 0.227 | runs/wo-gh-1/deployer.packet.md | null |
| observer | executed | 21099.816 | runs/wo-gh-1/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 2 reviews, expected 5.)
- Human gate: Verdict approved, but the work order carries the risk hint 'secrets', so a human is required.
