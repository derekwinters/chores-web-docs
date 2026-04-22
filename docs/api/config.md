# Config & Health

## GET /config
Get system configuration.

**Response (200):**
```json
{
  "admin_theme": "string"
}
```

## PUT /config
Update system configuration. Admin only.

**Request:**
```json
{
  "admin_theme": "string|null"
}
```

**Response (200):** Updated config

---

## GET /health
Health check.

**Response (200):**
```json
{
  "status": "ok"
}
```
