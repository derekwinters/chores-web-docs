# Deployment Operations

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

### Prometheus Scraping

The backend exposes a Prometheus metrics endpoint at `GET /metrics` (public, no authentication).

Example `prometheus.yml` scrape configuration:

```yaml
scrape_configs:
  - job_name: chores-web
    static_configs:
      - targets:
          - backend:8000   # use your backend host/port
    metrics_path: /metrics
    scrape_interval: 30s
```

Available application metrics:
- `chores_total{state, disabled}` — chore counts by state and disabled flag
- `chores_due_now_total` — chores currently due
- `chores_due_soon_total` — chores due within the configured `due_soon_days` window
- `chores_due_now_by_person{person}` — due chores per assignee
- `people_total` — registered user count
- `points_awarded_total` — total points across all PointsLog entries
- `chore_completions_by_person{person, window}` — completions per person for 7d and 30d windows

Process and HTTP request metrics are also included automatically.

No Docker Compose Prometheus service is bundled — add your own Prometheus container or use an external Prometheus instance pointing at the backend.
