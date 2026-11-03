# Operator notes

## Pinned upstream

- Repository: NVIDIA/auto-ontology
- Commit: cdaf61e1bd0cf3820d11d72b43bb460816aebbd3

The evaluation is only valid against this commit. If upstream moves, the pin is reviewed and updated in the spec first, never silently.

## Execution blockers (as filed, 2026-11-03)

1. The factory AI Gateway balance was exhausted on 2026-11-03, so the line's agent stations cannot execute.
2. The NVIDIA_API_KEY repository secret does not exist yet on arananet/auto-ontology-eval, so the S1 and S3 steps have no hosted NIM key to run with.

Nothing has been triggered: the run branch has not been pushed, no workflow has been dispatched, and no label has been applied to the issue.

## The exact next step that fires the run

Once both blockers clear (gateway balance restored, and the NVIDIA_API_KEY secret set on this repository), create the branch `anvil/run-auto-ontology-eval` from `main` and push it. That push is the trigger for `.github/workflows/anvil-execute.yml`, which runs work order wo-gh-1 (`work-orders/issue-1.json`) on the sdlc-default pipeline in execute mode and commits the run evidence back to the branch.
