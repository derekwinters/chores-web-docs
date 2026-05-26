# Deployment Maintenance

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
