#!/usr/bin/env python3
"""Seed deterministic, idempotent demo data for documentation screenshots.

This talks to the *running published backend* over its public HTTP API — it
never touches the database directly — so the data it produces matches what a
real deployment would show. Re-running it is safe: every write tolerates the
"already exists" (409) response, so the demo data (and therefore the captured
screenshots) is reproducible.

Bootstrapping the first admin
-----------------------------
The backend has no separate "create admin" step. `POST /v1/auth/login`
auto-creates the *first* user as an admin the first time it is called against
an empty database (see chores-web-backend app/routers/auth.py). So the very
first login with the configured admin username/password both creates and
authenticates the admin in one call. Subsequent runs simply log in.

Usage:
    python seed_demo_data.py [--base-url http://localhost:8000]

`--base-url` points at the backend's own port (8000). It can also point at the
frontend proxy (http://localhost:3000/api) — the versioned routes live under
`/v1/...` in both cases.
"""
from __future__ import annotations

import argparse
import sys

import httpx

# Backend's own port. The compose stack publishes the backend on 8000 and the
# frontend (nginx) on 3000; the frontend proxies /api -> backend, so
# http://localhost:3000/api is an equivalent target.
DEFAULT_BASE_URL = "http://localhost:8000"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpass123"

# The site's default light palette (owned by chores-web-design-tokens, vendored
# in the backend as app/data/themes.json). Forcing it makes the light-theme
# screenshots deterministic regardless of prior runs.
LIGHT_THEME_ID = "paper"

# Fixed demo people. Order and values are frozen so screenshots don't drift.
PEOPLE = [
    {"name": "Alex", "username": "alex", "password": "alex_pass"},
    {"name": "Bailey", "username": "bailey", "password": "bailey_pass"},
    {"name": "Charlie", "username": "charlie", "password": "charlie_pass"},
    {"name": "Dana", "username": "dana", "password": "dana_pass"},
]

# Fixed demo chores covering every assignment type and schedule kind so the
# screenshots exercise the full UI.
CHORES = [
    {
        "name": "Vacuum downstairs",
        "schedule_type": "weekly",
        "schedule_config": {"days": ["mon", "thu"]},
        "assignment_type": "rotating",
        "eligible_people": ["Alex", "Bailey", "Charlie", "Dana"],
        "points": 3,
    },
    {
        "name": "Clean bathrooms",
        "schedule_type": "weekly",
        "schedule_config": {"days": ["sat"]},
        "assignment_type": "rotating",
        "eligible_people": ["Alex", "Bailey"],
        "points": 5,
    },
    {
        "name": "Mow lawn",
        "schedule_type": "interval",
        "schedule_config": {"days": 14},
        "assignment_type": "fixed",
        "assignee": "Alex",
        "eligible_people": [],
        "points": 4,
    },
    {
        "name": "Take out trash",
        "schedule_type": "weekly",
        "schedule_config": {"days": ["wed"]},
        "assignment_type": "open",
        "eligible_people": [],
        "points": 1,
    },
]

# One fixed points award per person so the leaderboard and points log are
# populated deterministically.
POINT_AWARDS = [
    {"person": "alex", "points": 12, "reason": "Welcome bonus"},
    {"person": "bailey", "points": 8, "reason": "Extra help this week"},
    {"person": "charlie", "points": 5, "reason": "Tidied the garage"},
]


def _ok(status: int) -> bool:
    return status in (200, 201)


def seed(base_url: str) -> None:
    with httpx.Client(base_url=base_url, timeout=30) as client:
        # ------------------------------------------------------------------
        # Step 1: Login. First login against an empty DB auto-creates admin.
        # ------------------------------------------------------------------
        print(f"Logging in as '{ADMIN_USERNAME}' at {base_url} ...")
        login = client.post(
            "/v1/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        )
        if login.status_code != 200:
            print(f"Login failed: {login.status_code} {login.text}", file=sys.stderr)
            sys.exit(1)
        token = login.json()["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})
        print("Login OK (admin bootstrapped on first run)")

        # ------------------------------------------------------------------
        # Step 2: Force the light default theme for reproducible captures.
        # ------------------------------------------------------------------
        theme = client.put(f"/v1/theme/default/{LIGHT_THEME_ID}")
        if _ok(theme.status_code):
            print(f"Default theme set to '{LIGHT_THEME_ID}' (light)")
        else:
            # Non-fatal: 'paper' is the site default anyway.
            print(
                f"Could not set theme '{LIGHT_THEME_ID}': "
                f"{theme.status_code} {theme.text} (continuing)",
                file=sys.stderr,
            )

        # ------------------------------------------------------------------
        # Step 3: People (idempotent — 409 means already present).
        # ------------------------------------------------------------------
        for person in PEOPLE:
            r = client.post("/v1/people", json=person)
            if _ok(r.status_code):
                print(f"Person {person['name']}: created")
            elif r.status_code == 409:
                print(f"Person {person['name']}: already exists, skipping")
            else:
                print(
                    f"Person {person['name']}: {r.status_code} {r.text}",
                    file=sys.stderr,
                )

        # ------------------------------------------------------------------
        # Step 4: Chores (idempotent).
        # ------------------------------------------------------------------
        chore_ids: dict[str, int] = {}
        for chore in CHORES:
            r = client.post("/v1/chores", json=chore)
            if _ok(r.status_code):
                chore_ids[chore["name"]] = r.json()["id"]
                print(f"Chore '{chore['name']}': created")
            elif r.status_code == 409:
                print(f"Chore '{chore['name']}': already exists, skipping")
            else:
                print(
                    f"Chore '{chore['name']}': {r.status_code} {r.text}",
                    file=sys.stderr,
                )

        # Fill in ids for chores that already existed, so activity seeding can
        # still run on a re-invocation.
        if len(chore_ids) < len(CHORES):
            listing = client.get("/v1/chores")
            if _ok(listing.status_code):
                by_name = {c["name"]: c["id"] for c in listing.json()}
                for chore in CHORES:
                    chore_ids.setdefault(chore["name"], by_name.get(chore["name"]))

        # ------------------------------------------------------------------
        # Step 5: Complete one chore so the Board / Log show real activity.
        # Completing is naturally idempotent for a screenshot: re-completing a
        # freshly-scheduled occurrence just adds another identical log entry,
        # so we only complete when the chore is currently 'due'.
        # ------------------------------------------------------------------
        vacuum_id = chore_ids.get("Vacuum downstairs")
        if vacuum_id:
            current = client.get(f"/v1/chores/{vacuum_id}")
            if _ok(current.status_code) and current.json().get("state") == "due":
                done = client.post(
                    f"/v1/chores/{vacuum_id}/complete",
                    json={"completed_by": "alex"},
                )
                print(f"Complete 'Vacuum downstairs': {done.status_code}")
            else:
                print("'Vacuum downstairs' not due, skipping completion")

        # ------------------------------------------------------------------
        # Step 6: One-time point awards (Credits). Idempotent guard: only award
        # if the person has no awarded credits yet, so the leaderboard totals
        # stay fixed across re-runs.
        # ------------------------------------------------------------------
        existing = client.get("/v1/points")
        awarded_totals = {}
        if _ok(existing.status_code):
            awarded_totals = {row["person"]: row["total_points"] for row in existing.json()}
        for award in POINT_AWARDS:
            # A person with a leaderboard total already at/above this award has
            # been seeded before — skip to keep totals deterministic.
            if awarded_totals.get(award["person"], 0) >= award["points"]:
                print(f"Award to {award['person']}: already seeded, skipping")
                continue
            r = client.post("/v1/points/award", json=award)
            if _ok(r.status_code):
                print(f"Award {award['points']}pt to {award['person']}: created")
            else:
                print(
                    f"Award to {award['person']}: {r.status_code} {r.text}",
                    file=sys.stderr,
                )

        print("\nSeed complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    seed(args.base_url)


if __name__ == "__main__":
    main()
