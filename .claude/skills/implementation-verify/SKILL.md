---
name: implementation-verify
description: Re-run the strict docs build and show a changed-files summary for user review
---

# Implementation Verify Skill

Re-runs `mkdocs build --strict` to confirm the docs still build, then shows a
summary of changed files for user review.

**Verify reuses the strict build — no second command is invented.** This repo
has no test suite, so the verify state collapses into the test state: it runs
the exact same `mkdocs build --strict` again and adds a changed-files summary.
The state machine still passes through build-verify, but the command is
identical to the test state.

## Usage

```
/implementation-verify <issue-number>
```

## Workflow

1. **Build**: `mkdocs build --strict` (the same command as the test state)
2. **Verify build succeeded**: Check exit code, report any strict-mode failures
3. **Prepare changes summary**:
   - List all files modified (`git diff --stat`)
   - Show line change counts
   - Summarize the docs changes (page, nav entry, API reference, blog)
   - Note the strict-build result
4. **Pause workflow**: Wait for user approval or request for changes

## Parameters

- `issue_number` (optional): For reference in output

## Output

Shows:
- Files modified with line counts
- Implementation summary
- Strict-build result
- Ready for user to:
  - Approve for commit
  - Request more changes
  - Abort

## Notes

- Called by orchestrator after the test state passes
- Verify == test for this repo: it re-runs `mkdocs build --strict` (no new
  command) and the added value is the changed-files summary for review
- Shows all changes before the user reviews
- User has the control point here
