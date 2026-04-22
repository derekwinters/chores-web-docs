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

### Styling

- Use CSS files (e.g., `MyComponent.css`)
- Reference CSS variables: `var(--bg)`, `var(--accent)`, etc.
- Mobile-first responsive design
- Theme colors already defined in `App.css`

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
