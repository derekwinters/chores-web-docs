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

### Environment Variables

**Backend (.env or compose):**
```
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Frontend (vite.config.js):**
```javascript
VITE_API_URL=http://backend:8000/api
```

### Database

- **Development:** SQLite in `backend/app.db`
- **Production:** Can use PostgreSQL by changing DATABASE_URL
  ```
  DATABASE_URL=postgresql://user:pass@host/dbname
  ```

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

### Database Lock

```bash
# Reset database
docker-compose exec backend rm app.db
docker-compose exec backend python -c "from app.database import engine; ..."
```

### CORS Errors

1. Check frontend `VITE_API_URL` points to backend
2. Verify backend CORS middleware allows frontend origin
3. Check browser console for actual error

### Authentication Issues

1. Check token in localStorage: `localStorage.getItem('token')`
2. Verify token in Authorization header: `Authorization: Bearer <token>`
3. Check token hasn't expired (365 days)
4. Verify user still exists in database

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

## Production Checklist

- [ ] SSL/HTTPS configured
- [ ] CORS origins restricted
- [ ] Database backups automated
- [ ] Monitoring/alerting set up
- [ ] Log aggregation configured
- [ ] Authentication tokens secure
- [ ] Regular security updates
- [ ] Disaster recovery plan tested
- [ ] Rate limiting enabled (if needed)
- [ ] Health checks monitoring
