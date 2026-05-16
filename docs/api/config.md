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

## GET /config/updates/status
Get current update check status. Admin only.

**Response (200):**
```json
{
  "last_check": "ISO8601|null",
  "available_version": "string|null",
  "is_checking": boolean,
  "enabled": boolean,
  "interval_hours": integer
}
```

## POST /config/updates/check
Manually trigger an update check. Admin only.

**Response (200):** Updated status (see above)

## PUT /config/updates/config
Configure automatic update checking. Admin only.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `enabled` | boolean | Enable/disable automatic checks |
| `interval_hours` | integer | Check interval in hours |

**Response (200):** Updated configuration

---

## GET /health
Health check.

**Response (200):**
```json
{
  "status": "ok"
}
```
