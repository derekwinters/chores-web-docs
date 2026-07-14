---
name: implementation-test
description: Run the strict docs build for implemented changes
---

# Implementation Test Skill

Runs `mkdocs build --strict` to verify implemented changes. This repo has no
test suite — the strict build is the PR gate (see `CLAUDE.md`).

## Usage

```
/implementation-test
```

## Workflow

1. **Run the strict build**: `mkdocs build --strict` (from the repo root)
2. **Capture output**: warnings promoted to errors, first failing message
3. **Check exit code**: 0 = success, non-zero = failure
4. **Report results**:
   - If PASS: The strict build passed. Ready for verification.
   - If FAIL: List the strict-mode failures (broken nav refs, bad links,
     snippet `check_paths` errors). Blocks workflow.

## Output

- ✅ Strict build passed
  - `mkdocs build --strict` clean
  - Ready for next phase
- ❌ Strict build failed
  - The failing messages (nav/link/snippet errors)
  - Blocks workflow until fixed

## Error Handling

If the strict build fails:
- Report exactly which strict-mode failures occurred
- Show the mkdocs error output
- Pause workflow for user review and fixes

## Notes

- Called by orchestrator after implementation
- The strict build must pass before proceeding
- Can be called independently to verify changes
- `mkdocs build --strict` promotes warnings (dead links, missing nav targets,
  unresolved snippet paths) to hard errors — that is exactly the CI gate
