# CLAUDE.md — Developer and AI Agent Reference

This repo is the USER-FACING documentation for chores-web (mkdocs-material,
deployed with mike for versioned docs) — and it OWNS the API contract.

## API Contract Ownership (contract-first)

- `API_VERSION` (repo root) — the current API major version.
- `docs/api/openapi.json` — the golden OpenAPI snapshot.

`chores-web-backend` CI checks out this repo on every PR and runs `oasdiff`
between this golden snapshot and the backend's live schema. A breaking
change in the backend CANNOT merge until a PR here has:

1. Incremented `API_VERSION` (e.g., `1` → `2`).
2. Updated `docs/api/openapi.json` (generated in the backend repo with
   `python scripts/generate_openapi.py`).

What counts as breaking: removing an endpoint/method, adding a required
request parameter or body field, changing a response field type, renaming a
path parameter, removing a response field. NOT breaking: new endpoints, new
optional parameters or response fields, error message wording.

## Scope

User-facing content only: user guide, deployment, API reference, release
blog. Developer-internal docs (architecture, ADRs, developer guides) live
in the code repos (`chores-web-backend`, `chores-web-frontend`).

## Versioned Docs

Deploys use mike; the docs version tracks the API major version
(`v1`, `v2`, ...) with the `latest` alias. Bumping `API_VERSION` starts a
new docs version tree on the next deploy.

## Build

`mkdocs build --strict` must pass — it is the PR gate.
