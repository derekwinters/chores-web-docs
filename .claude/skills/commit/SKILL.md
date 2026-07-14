---
name: commit
description: Run the strict docs build and create a conventional commit with proper type and scope
---

# Commit Skill

Validates that `mkdocs build --strict` passes, then creates a Conventional
Commit with proper type/scope. This repo has no test suite — the strict build
is the gate (see `CLAUDE.md`).

## Usage

```
/commit
```

## Flow

1. Run the strict build (`mkdocs build --strict`)
2. Stop if the build fails — report the strict-mode failures
3. Review staged/unstaged changes
4. Derive commit type and scope from changes
5. Create commit using Conventional Commits format

## Commit Format

```
<type>(<scope>): <short description>

[optional body explaining why]
```

## Types

Valid types (per `CLAUDE.md`): `feat`, `fix`, `chore`, `ci`, `docs`, `build`,
`refactor`, `test`, `perf`, `revert`.

- `docs` - documentation content (the natural type for most changes here)
- `feat` - a new user-facing capability documented
- `fix` - correcting wrong/misleading documented behavior
- `chore` - tooling, `.claude/` machinery, deps
- `ci` - CI/workflow changes
- `build` - mkdocs/mike build configuration
- `refactor` - restructuring docs without changing meaning
- `perf` - performance-related content or config
- `revert` - reverting a previous commit

## Scopes

- `guide` - user guide pages
- `api` - API reference, `docs/api/openapi.json`, `API_VERSION`
- `blog` - release blog posts
- `nav` - `mkdocs.yml` navigation and site config
- `agents` - `.claude/` agents and skills machinery
- Use the most relevant scope

## Rules

- Subject line ≤72 characters, lowercase, no period
- Imperative mood: "add" not "added"
- Body only when "why" is non-obvious
- Stage changes before invoking
