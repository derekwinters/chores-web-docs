# Developer Guide

## Prerequisites

- Node.js 16+ (for frontend)
- Python 3.11+ (for backend)
- Git

## Local Development Setup

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Swagger UI:** http://localhost:8000/docs

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Development URL:** http://localhost:5173

### First-Time Setup

1. Start backend (opens on :8000)
2. Start frontend (opens on :5173)
3. Frontend will redirect to setup page if no users exist
4. Create first admin user through setup page
5. Login with created credentials

## Issue Lifecycle

All work in this repository follows a 4-stage lifecycle controlled by GitHub issue labels.

### Stages

| Stage | Label | Description |
|-------|-------|-------------|
| 1. Concept | *(none)* | Raw idea recorded, not yet triaged |
| 2. Context & Assignment | `ready-to-grill` | Triage complete, milestone assigned |
| 3. Grilling Complete | `ready-for-work` | Grilling done, implementation contract exists |
| 4. In Development | `in-development` | Agent actively working on the issue |

A stage must not begin unless the proper label is assigned.

### Agents & Entry Points

| Agent | Trigger | Action |
|-------|---------|--------|
| `github-issue-triage-orchestrator` | Manual or webhook | Triages issue, assigns milestone, applies `ready-to-grill` |
| `/grill-with-docs issue <N>` | Manual | Runs grilling session, posts structured comment, flips label to `ready-for-work` |
| `github-issue-implementation-orchestrator` | Manual | Implements issue end-to-end via TDD, creates PR |

### Grilling

Grilling is required before development begins. Run `/grill-with-docs issue <N>` to:

1. Conduct a structured session covering all 4 areas: backend, database, frontend, docs
2. Post a structured grilling comment on the issue (decisions, impact areas, behaviors checklist)
3. Remove `ready-to-grill`, apply `ready-for-work`

### Development

The implementation orchestrator handles all development autonomously:

1. Validates `ready-for-work` label and grilling comment presence
2. Creates `<type>-issue-<N>` branch from updated main
3. Drafts documentation updates (`docs:` commit)
4. Runs TDD loop — derives behaviors from grilling checklist, red-green-refactor cycles
5. Full test suite must pass
6. Docker verify + user approval pause
7. Code commit (`feat:/fix:/refactor:`)
8. Doc-validate — reconciles docs against implementation
9. Push + PR creation (removes `in-development`)

## Development Workflow

### Running Tests

**Frontend:**
```bash
cd frontend
npm test                 # Watch mode
npm test -- --run      # Single run
```

**Tests must pass before committing.**

### Making Changes

1. **Frontend Changes:**
   - Edit components/pages in `src/`
   - Tests automatically re-run
   - Ensure tests pass: `npm test -- --run`
   - Commit only if tests pass (205/205)

2. **Backend Changes:**
   - Edit routers/services in `app/`
   - Server auto-reloads with `--reload`
   - Test via Swagger UI or API client
   - Add appropriate logging to ChoreLog
   - Ensure database migrations work

3. **Database Schema Changes:**
   - Add/modify fields in `models.py`
   - Update corresponding schemas in `schemas.py`
   - Tables auto-create on startup (see `lifespan` in `main.py`)
   - Add migration scripts if needed for existing data

### Commit Guidelines

- **Title:** Short, imperative mood ("add feature", "fix bug", "refactor component")
- **Body:** Explain *why* not *what* (code shows what)
- **Test Status:** Include "Frontend tests: 205/205 passing ✓" if applicable
- **Co-authored:** End with "Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"

Example:
```
feat: add theme deletion for custom themes

- Add DELETE /theme/delete/{theme_id} endpoint
- Prevent deletion of default themes (dark, light, ocean)
- Switch to dark theme if current is deleted
- Add confirmation modal in ThemeSettings component
- Add 3 tests for deletion functionality

Frontend tests: 205/205 passing ✓

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

## Observability

### Metrics Endpoint

The backend exposes a Prometheus-compatible metrics endpoint:

**`GET /metrics`** — Returns metrics in Prometheus text format. Public, no authentication required.

Available metrics:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `chores_total` | Gauge | `state`, `disabled` | Total chores grouped by state and disabled flag |
| `chores_due_now_total` | Gauge | — | Chores where `state='due'` |
| `chores_due_soon_total` | Gauge | — | Chores where `next_due <= today + due_soon_days` |
| `chores_due_now_by_person` | Gauge | `person` | Due chores grouped by current assignee |
| `people_total` | Gauge | — | Total user count |
| `points_awarded_total` | Gauge | — | Sum of all PointsLog entries |
| `chore_completions_by_person` | Gauge | `person`, `window` | Completions in 7d and 30d windows |

Process metrics (CPU, memory, file descriptors) are provided automatically by `prometheus_client`.

HTTP request metrics (request count, duration histogram by path) are provided by `starlette-prometheus` middleware.

## API Development

### Adding a New Endpoint

1. **Define Schema** (in `schemas.py`):
   ```python
   class NewThingOut(BaseModel):
       id: int
       name: str
       model_config = {"from_attributes": True}
   ```

2. **Add Router Handler** (in `routers/`):
   ```python
   @router.get("", response_model=list[NewThingOut], summary="List all things")
   async def list_things(
       current_user: str = Depends(get_current_user),
       db: AsyncSession = Depends(get_db),
   ):
       """Get all things. Optionally filtered by query params."""
       # Implementation
   ```

3. **Add Service Logic** (if complex, in `services/`):
   ```python
   async def process_thing(thing: Thing, db: AsyncSession) -> Thing:
       # Business logic here
       await _log_action(thing, "processed", "user", db)
       db.add(thing)
       await db.commit()
       return thing
   ```

4. **Add to Main App** (already done if using include_router):
   - Routers are auto-included in `main.py`

5. **Document** (in `docs/API.md`):
   - Add endpoint documentation with example request/response

6. **Test** (in Swagger UI):
   - Verify endpoint works before committing

### Logging Actions

All user-visible actions should be logged:

```python
await _log_action(
    chore=chore_obj,
    action="completed",           # Action type
    person="username",            # Username or "system"
    db=db,
    reassigned_to=None,          # Optional, for reassignment
)
```

## React Component Development

### Component Structure

```typescript
// src/components/MyComponent.tsx
import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getThings, updateThing } from "../api/client";
import "./MyComponent.css";

interface Thing {
  id: number;
  name: string;
}

export default function MyComponent() {
  const { data: things = [], isLoading } = useQuery({
    queryKey: ["things"],
    queryFn: getThings,
  });

  const mutation = useMutation({
    mutationFn: updateThing,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["things"] });
    },
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {things.map(thing => (
        <div key={thing.id}>{thing.name}</div>
      ))}
    </div>
  );
}
```

### Component Testing

```typescript
// src/__tests__/MyComponent.test.jsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import MyComponent from "../components/MyComponent";
import * as client from "../api/client";

vi.mock("../api/client");

function wrap(ui) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("MyComponent", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    client.getThings.mockResolvedValue([]);
  });

  it("renders empty state", async () => {
    wrap(<MyComponent />);
    await waitFor(() => expect(screen.getByText("Loading...")).not.toBeInTheDocument());
  });
});
```

### Styling & Theming

- Use CSS files (e.g., `MyComponent.css`)
- **Always use CSS variables for colors:** `var(--bg)`, `var(--accent)`, etc.
- **Never hardcode hex values** – breaks theme switching
- Mobile-first responsive design
- Theme colors defined in `App.css` via 9-color system

#### 9-Color Theme System

All application theming uses a unified 9-color palette:

| Variable | Purpose |
|----------|---------|
| `--bg` | Page background |
| `--surface` | Card/panel background (layer 1) |
| `--surface2` | Elevated surface (layer 2), inputs, tags |
| `--accent` | Highlights, links, focus rings |
| `--primary` | Primary buttons and controls |
| `--secondary` | Secondary buttons |
| `--success` | Positive states |
| `--warning` | Caution states |
| `--error` | Destructive actions / validation errors |

**Rules:**
- Use `--primary` for buttons (not `--accent`)
- Use `--accent` for links and highlights (not `--primary`)
- Use `--error` for destructive actions (no `--danger`)
- For semi-transparent overlays: `rgba(var(--error-rgb), <alpha>)`

See `.claude/skills/theme-guide/SKILL.md` for complete reference.

## Debugging

### Frontend

```typescript
// In browser DevTools:
// - React DevTools extension
// - Redux DevTools (React Query tab)
// - Console for network requests
console.log("Debug:", thing);
```

### Backend

```python
# In code
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Processing thing: {thing}")

# In terminal with --reload
# Server logs appear in terminal
```

## Performance Tips

1. **React Query:** Use proper query keys to avoid unnecessary fetches
2. **Memoization:** Use `useMemo` for expensive computations
3. **Invalidation:** Be specific with `invalidateQueries` (use queryKey prefix)
4. **Database:** Use async queries, avoid N+1 problems
5. **Images:** Optimize before uploading

## Security Checklist

- [ ] Validate all inputs (Pydantic handles backend)
- [ ] Check auth on all endpoints (`get_current_user` dependency)
- [ ] Prevent admin-only operations from regular users
- [ ] Sanitize/escape any user-generated content
- [ ] Use HTTPS in production (see DEPLOYMENT.md)

## Common Tasks

### Add a new field to Chore

1. Add to `models.py` Chore class:
   ```python
   new_field: Mapped[str] = mapped_column(Text, default="")
   ```

2. Add to `schemas.py` ChoreOut:
   ```python
   new_field: str
   ```

3. Add to ChoreCreate/ChoreUpdate if user-settable:
   ```python
   new_field: Optional[str] = None
   ```

4. Database auto-creates column on next startup

### Add a new action type

1. Add constant to `chore_service.py`:
   ```python
   CHANGE_THING = "thing"
   ```

2. Call in service function:
   ```python
   await _log_action(chore, CHANGE_THING, "system", db)
   ```

3. Update `docs/API.md` to document new action type

### Create a new page

1. Create in `src/pages/MyPage.tsx`
2. Import in `src/App.jsx`
3. Add route in router setup
4. Add navigation link in `src/components/Sidebar.tsx`
5. Create tests in `src/__tests__/MyPage.test.jsx`

## Troubleshooting

### Frontend tests failing
- Run `npm test -- --run` to see full output
- Check test mocks are set up correctly
- Ensure React Query queryClient is in test wrapper

### Backend startup issues
- Check `requirements.txt` installed: `pip list`
- Verify Python 3.11+: `python --version`
- Check port 8000 not in use: `lsof -i :8000`

### Database errors
- Delete `backend/app.db` to reset database
- Check models.py has no syntax errors
- Verify schema migrations don't break existing data

### Performance issues
- Check React Query DevTools (browser extension)
- Profile with browser DevTools Perf tab
- Check backend logs for slow queries
- Verify indexes on frequently-queried columns

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [React Query Docs](https://tanstack.com/query/latest)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Vitest Docs](https://vitest.dev/)
