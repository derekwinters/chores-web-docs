# Documentation screenshot tooling

Automated, reproducible screenshots for the user guide. The pipeline boots the
**published compose stack** (the exact images users deploy), seeds deterministic
demo data through the API, and captures each main sidebar page in the light
theme. Generated PNGs are committed under `docs/assets/screenshots/` and wired
into the doc pages.

## Pieces

| File | Role |
|------|------|
| `screenshots.config.json` | Single source of truth: admin creds, viewport, the routes to capture, and which doc page references which PNG. |
| `seed_demo_data.py` | Idempotent API seed — people, chores, activity, point awards, and forces the light default theme. |
| `capture_screenshots.mjs` | Playwright/Chromium capture — logs in, forces the light colour scheme, screenshots each route to `docs/assets/screenshots/`. |
| `wire_screenshots.py` | Rewrites the `<!-- screenshots:auto:START/END -->` block in each target doc page, referencing only PNGs that exist (so `mkdocs build --strict` never breaks). |

## Regenerate on demand (recommended: CI)

The normal way to regenerate is the **Documentation Screenshots** workflow
(`.github/workflows/screenshots.yml`), run from the Actions tab
(`workflow_dispatch`). Pick the branch to capture on; the workflow boots the
stack, seeds, captures, wires the docs, verifies `mkdocs build --strict`, and
commits the regenerated PNGs back to that branch.

The stack needs a `JWT_SECRET`. The workflow uses the optional
`SCREENSHOTS_JWT_SECRET` repo secret if present, otherwise generates a random
one per run (the stack is ephemeral, so a throwaway secret is fine).

> The first successful run is what populates `docs/assets/screenshots/` and
> fills in the image references in the user guide. Until then the marker blocks
> are intentionally empty and the strict build passes with no images.

## Regenerate locally

Requires Docker, Python 3.11+, and Node 20+.

```bash
# 1. Boot the published stack (from the deployment dir)
cd docs/deployment
echo "JWT_SECRET=$(openssl rand -hex 32)" > .env
docker compose up -d --wait
cd ../..

# 2. Seed deterministic demo data
pip install -r scripts/requirements.txt
python scripts/seed_demo_data.py --base-url http://localhost:8000

# 3. Capture screenshots
cd scripts
npm install
npx playwright install --with-deps chromium
node capture_screenshots.mjs
cd ..

# 4. Wire the PNGs into the docs and verify the strict build
python scripts/wire_screenshots.py
mkdocs build --strict

# 5. Tear down
cd docs/deployment && docker compose down -v
```

Everything is deterministic and idempotent: re-running produces the same demo
data and therefore the same screenshots.

## Pages captured

Enumerated from the frontend sidebar navigation (`src/App.jsx`):

- **Board** (`/`) — the dashboard
- **Chores** (`/chores`)
- **Users** (`/users`, admin only)
- **Log** (`/log`)
- **Settings** (`/settings/general`, reached from the user menu)

Add or remove entries by editing `captures` (and `wiring`) in
`screenshots.config.json` — the capture and wiring scripts follow it.
