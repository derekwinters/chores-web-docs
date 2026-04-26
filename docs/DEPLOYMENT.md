# Deployment

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
| `JWT_SECRET` | string | Yes (prod) | auto-generated | your-secret-key-here | Secret for JWT token signing |
| `JWT_EXPIRATION_DAYS` | int | No | `365` | `365` | JWT token expiration in days |

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

## Security

### HTTPS

1. Obtain SSL certificate (Let's Encrypt recommended)
2. Mount cert in nginx container:
   ```yaml
   volumes:
     - /etc/letsencrypt/live/yourdomain:/etc/ssl/certs
   ```

3. Configure nginx SSL:
   ```nginx
   server {
     listen 443 ssl;
     server_name yourdomain.com;
     ssl_certificate /etc/ssl/certs/fullchain.pem;
     ssl_certificate_key /etc/ssl/certs/privkey.pem;
     # ... rest of config
   }
   ```

### Authentication

- JWT tokens expire after 365 days
- Tokens stored in localStorage (frontend)
- Token blacklist tracks logouts
- Passwords hashed with bcrypt (after SHA256 pre-hash)

### CORS

Default allows all origins in development. For production:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Backup & Recovery

### Backup Database

```bash
# Backup SQLite
docker-compose exec backend cp app.db app.db.backup

# Restore from backup
docker-compose exec backend cp app.db.backup app.db
```

### Backup Data

```bash
# Create backup archive
docker-compose exec backend tar czf app.db.tar.gz app.db

# Download backup
docker cp <container>:/app/app.db.tar.gz ./backup.tar.gz
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs

```bash
# Frontend logs
docker-compose logs frontend

# Backend logs
docker-compose logs backend -f

# All logs
docker-compose logs -f
```

### Metrics

Monitor via docker stats:
```bash
docker stats
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 <PID>
```

### PostgreSQL Connection Issues

```bash
# Verify PostgreSQL is running
docker-compose ps | grep db

# Check logs
docker-compose logs db

# Test connection from backend
docker-compose exec backend python -c \
  "from app.database import engine; \
   import asyncio; \
   asyncio.run(engine.connect())"
```

**Common issues:**
- DATABASE_URL format incorrect (missing `+asyncpg`)
- PostgreSQL password wrong
- Database user missing CREATE privilege
- Port 5432 not exposed or already in use
- Network connectivity between containers

### Database Performance Issues

**Slow queries:**
```bash
# Enable query logging in PostgreSQL
# Add to docker-compose.yml postgres environment:
POSTGRES_INIT_ARGS: "-c log_statement=all"

# Check logs
docker-compose logs db | grep query
```

**Connection pool issues:**
```bash
# Check active connections
docker-compose exec db psql -U chores -d chores \
  -c "SELECT count(*) FROM pg_stat_activity;"
```

### CORS Errors

1. Check frontend `VITE_API_URL` points to backend (should match `CORS_ORIGINS`)
2. Verify backend CORS middleware allows frontend origin in docker-compose.yml
3. Check browser console Network tab for actual error (look at Preflight OPTIONS request)
4. Production: ensure CORS_ORIGINS uses HTTPS if frontend is HTTPS

**Fix:**
```yaml
# docker-compose.yml
backend:
  environment:
    CORS_ORIGINS: "https://yourdomain.com"  # Must match frontend origin exactly
```

### Authentication Issues

1. **Token not present:**
   - Check token in localStorage: `localStorage.getItem('token')`
   - Verify login was successful (check network tab)
   - Check browser accepts/sends cookies

2. **Invalid token:**
   - Verify token in Authorization header: `Authorization: Bearer <token>`
   - Check token format (should be JWT, not just a string)
   - Verify JWT_SECRET matches between deployments

3. **Token expired:**
   - Check token expiration: `jwt.decode(token, options={"verify_signature": False})`
   - JWT tokens expire after 365 days, user must login again
   - For long-lived sessions, consider refresh token pattern

4. **User no longer exists:**
   - Verify user still exists in database
   - Check if user was deleted after login
   - Verify username matches between frontend and backend

**Debug auth issues:**
```bash
# Check token blacklist
docker-compose exec db psql -U chores -d chores \
  -c "SELECT * FROM token_blacklist;"

# Check active users
docker-compose exec db psql -U chores -d chores \
  -c "SELECT id, username, is_admin FROM person;"
```

### Container Startup Issues

```bash
# View startup logs
docker-compose logs backend --tail 100

# Common errors:
# "Connection refused" - database not ready
#   Solution: Wait for db container to be healthy, check logs
# "Address already in use" - port conflict
#   Solution: Change ports in docker-compose.yml or kill existing process
# "Schema mismatch" - database schema outdated
#   Solution: Backend auto-creates schema on startup, check db logs
```

### Network Issues Between Containers

```bash
# Test backend can reach database
docker-compose exec backend ping db

# Test frontend can reach backend
docker-compose exec frontend wget -O- http://backend:8000/health
```

## Scaling

### Horizontal Scaling

Use Docker Swarm or Kubernetes:
```bash
# Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.yml chores
```

### Database Scaling

For PostgreSQL with replication:
1. Set up primary/replica PostgreSQL
2. Update DATABASE_URL to primary
3. Configure read replicas for reporting queries

### Caching Layer

Add Redis for caching:
```yaml
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

Then implement caching in FastAPI:
```python
@app.get("/chores")
async def list_chores(cache: Redis = Depends(get_redis)):
    # Check cache first
    # Fall back to database
```

## Performance Tuning

### Database

- Add indexes on frequently-queried columns
- `next_due` and `state` benefit from indexes
- Monitor slow queries with logging

### Frontend

- Enable service worker caching
- Optimize bundle size (currently ~200KB)
- Use CDN for static assets

### Backend

- Use async database queries (already done)
- Connection pooling (SQLAlchemy handles this)
- Consider caching for read-heavy workloads

## Maintenance

### Regular Tasks

- **Daily:** Monitor logs for errors
- **Weekly:** Backup database
- **Monthly:** Review performance metrics
- **Quarterly:** Update dependencies

### Updates

1. Pull latest code
2. Run tests: `npm test -- --run`
3. Build images: `docker-compose build`
4. Stop old containers: `docker-compose down`
5. Start new containers: `docker-compose up -d`
6. Verify health: `curl localhost:8000/health`

### Zero-Downtime Updates

For critical deployments:

```bash
# Start new container
docker-compose up -d --scale backend=2

# When ready, remove old container
docker-compose down
```

## Disaster Recovery

### Steps to Recover

1. Stop containers: `docker-compose down`
2. Restore database from backup
3. Rebuild images: `docker-compose build`
4. Start services: `docker-compose up -d`
5. Verify: `curl localhost:8000/health`

### Data Loss Prevention

- Automatic daily backups
- Test restore procedure monthly
- Keep backups on separate system
- Document all manual changes to database

## Production Deployment Checklist

### Pre-Deployment (Before Deploy)
- [ ] Database fully backed up
- [ ] All tests passing locally (`npm test -- --run`)
- [ ] Code reviewed and approved
- [ ] Environment variables configured for production
- [ ] SSL/HTTPS certificates obtained and valid
- [ ] Disaster recovery plan documented and tested
- [ ] Rollback procedure documented
- [ ] All team members notified of deployment window

### During Deployment
- [ ] Monitor health endpoint during startup: `curl https://yourdomain.com/health`
- [ ] Check backend logs for errors: `docker logs <backend-container>`
- [ ] Verify frontend loads without errors (browser console check)
- [ ] Test login with known user account
- [ ] Verify API endpoints respond: `curl https://yourdomain.com/api/people`
- [ ] Check database connectivity and query performance
- [ ] Monitor system resources (CPU, memory, disk)

### Post-Deployment (After Deploy)
- [ ] Smoke test: Complete a full chore workflow
- [ ] Verify data integrity (check person count, chore count)
- [ ] Confirm backups still working
- [ ] Review monitoring dashboards (if configured)
- [ ] Check log aggregation system (if configured)
- [ ] Verify users can access from multiple browsers
- [ ] Document deployment completion and any issues
- [ ] Keep backup of pre-deployment database for 7 days minimum

### Ongoing Production Operations
- [ ] CORS origins restricted to your domain only
- [ ] Database backups scheduled and tested weekly
- [ ] Monitoring/alerting configured for uptime
- [ ] Log aggregation configured and reviewed regularly
- [ ] Authentication tokens using secure SECRET key (not default)
- [ ] Regular security updates (monthly review of dependencies)
- [ ] Health checks monitored (set up uptime monitoring service)
- [ ] Rate limiting enabled if public-facing
- [ ] Change password for default admin account
- [ ] Remove development/test data before going live
