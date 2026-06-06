# Deployment Setup

## Requirements

- Docker & Docker Compose
- (Optional) Domain name and SSL certificate for production

## Docker Deployment

### Development Deployment

```bash
docker-compose up
```

This starts:
- **Frontend:** http://localhost:3000 (Nginx reverse proxy)
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Production Deployment

1. **Update docker-compose.yml** for production:
   - Set `ENVIRONMENT=production`
   - Change frontend to serve from `/api` proxy
   - Enable HTTPS redirect
   - Set proper CORS origins

2. **Build images:**
   ```bash
   docker-compose -f docker-compose.yml build
   ```

3. **Start services:**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

4. **Verify health:**
   ```bash
   curl http://localhost:8000/health
   ```

## Configuration

### Environment Variables Reference

#### Backend Environment Variables

| Variable | Type | Required | Development | Production | Description |
|----------|------|----------|-------------|-----------|-------------|
| `DATABASE_URL` | string | Yes | `postgresql+asyncpg://chores:chores@db/chores` | `postgresql+asyncpg://user:pass@db.example.com/chores` | PostgreSQL async connection string |
| `CORS_ORIGINS` | string | Yes | `http://localhost:3000` | `https://yourdomain.com` | Frontend origin for CORS validation |
| `ENVIRONMENT` | string | Yes | `development` | `production` | Environment mode (affects logging, debug, etc.) |
| `LOG_LEVEL` | string | No | `INFO` | `INFO` or `WARNING` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `JWT_SECRET` | string | Yes | required, no default | `$(openssl rand -hex 32)` | Secret for JWT token signing — server fails to start if unset |
| `JWT_EXPIRATION_DAYS` | int | No | `365` | `365` | JWT token expiration in days |

**Generating a strong JWT secret:**
```bash
openssl rand -hex 32
```

> **Important:** Changing `JWT_SECRET` in production invalidates all existing sessions — all users must log in again. This is expected and acceptable when rotating the secret.

#### Frontend Environment Variables

| Variable | Type | Required | Development | Production | Description |
|----------|------|----------|-------------|-----------|-------------|
| `VITE_API_URL` | string | Yes | `http://backend:8000/api` | `https://yourdomain.com/api` | Backend API base URL |

### Database

**Primary Database: PostgreSQL**

Connection format:
```
postgresql+asyncpg://username:password@host:5432/database_name
```

**In docker-compose (development):**
```yaml
db:
  image: postgres:16-alpine
  environment:
    POSTGRES_USER: chores
    POSTGRES_PASSWORD: chores
    POSTGRES_DB: chores
```

**In production:**
- Use external PostgreSQL instance
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
