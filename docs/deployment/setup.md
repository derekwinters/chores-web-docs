# Deployment Setup

## Requirements

- Docker & Docker Compose
- (Optional) Domain name and SSL certificate for production

## Docker Deployment

The deployment stack is defined in [`docker-compose.yml`](docker-compose.yml),
which lives in this documentation repository at
[`docs/deployment/docker-compose.yml`](https://github.com/derekwinters/chores-web-docs/blob/main/docs/deployment/docker-compose.yml)
and ships with this site — download it from the link above. The full file is
embedded below, and it is smoke-tested in CI on every docs change: the stack
is booted from the published images and the health endpoints are asserted, so
the file you see here is known to work.

It runs three services from published images:

- **`frontend`** — `ghcr.io/derekwinters/chores-web-frontend` (Nginx serving
  the built app on port 3000, reverse-proxying `/api/` to the backend)
- **`backend`** — `ghcr.io/derekwinters/chores-web-backend` (FastAPI on
  port 8000)
- **`db`** — `postgres:16-alpine` with a named volume for data

```yaml
--8<-- "docs/deployment/docker-compose.yml"
```

### Development Deployment

```bash
# 1. Download the compose file (or clone this repo and cd docs/deployment)
curl -fsSLO https://raw.githubusercontent.com/derekwinters/chores-web-docs/main/docs/deployment/docker-compose.yml

# 2. Generate the required JWT secret
echo "JWT_SECRET=$(openssl rand -hex 32)" > .env

# 3. Start the stack
docker compose up -d
```

This starts:

- **Frontend:** http://localhost:3000 (Nginx reverse proxy)
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Production Deployment

1. **Pin image versions** — change both `image:` tags from `latest` to the
   same released version (e.g. `ghcr.io/derekwinters/chores-web-backend:2.2.0`)
   so upgrades are deliberate. Releases are listed on each repository's
   GitHub Releases page.

2. **Set a strong `JWT_SECRET`** in `.env` (see
   [Environment Variables](#environment-variables-reference) below).

3. **Use real database credentials** — either change the `db` service's
   `POSTGRES_*` values and the matching `DATABASE_URL`, or point
   `DATABASE_URL` at an external PostgreSQL instance and remove the `db`
   service.

4. **Terminate HTTPS in front of the stack** — put a TLS-terminating reverse
   proxy (or the nginx SSL configuration from
   [Operations → Security](operations.md#https)) in front of the frontend
   port.

5. **Start and verify:**
   ```bash
   docker compose up -d
   curl http://localhost:8000/health
   ```

## Configuration

### Environment Variables Reference

#### Backend Environment Variables

The backend reads exactly two settings (from the environment or a `.env`
file):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `postgresql+asyncpg://chores:chores@db/chores` | PostgreSQL async connection string |
| `JWT_SECRET` | Yes | — (server fails to start if unset) | Secret for JWT token signing |

**Generating a strong JWT secret:**
```bash
openssl rand -hex 32
```

> **Important:** Changing `JWT_SECRET` in production invalidates all existing
> sessions — all users must log in again. This is expected and acceptable
> when rotating the secret.

CORS is not configured via environment variables — the backend currently
allows all origins, and the bundled stack avoids cross-origin requests
entirely because Nginx proxies `/api/` to the backend on the same origin. To
restrict origins, see [Operations → CORS](operations.md#cors).

#### Frontend Environment Variables

The published frontend image needs no environment variables. API requests go
to `/api/v1` on the frontend's own origin, and Nginx proxies them to the
backend service.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | `/api/v1` | Build-time API base URL. Only relevant when building the frontend yourself; baked into the bundle at `npm run build`, not read at runtime. |

### Database

**Primary Database: PostgreSQL**

Connection format:
```
postgresql+asyncpg://username:password@host:5432/database_name
```

The bundled `db` service (see the compose file above) runs
`postgres:16-alpine` with a named volume, so data survives container
recreation.

**In production:**

- Use an external PostgreSQL instance, or at minimum change the bundled
  service's credentials
- Update DATABASE_URL with production credentials
- Ensure database user has CREATE/ALTER privileges for schema initialization
- Backend auto-creates tables on startup via SQLAlchemy
- No manual migrations needed (schema-first approach)

**Schema Overview:**

- **Person** – Users (id, name, username, password_hash, is_admin, color, goals, points)
- **Chore** – Task definitions (id, name, schedule_type, assignment_type, points, state)
- **PointsLog** – Point transactions (id, person_id, points, chore_id, completed_at)
- **ChoreLog** – Audit log (id, chore_id, person_id, action, timestamp)
- **Settings** – System config (key, value)
- **TokenBlacklist** – Invalidated tokens (token_jti, expires_at)
