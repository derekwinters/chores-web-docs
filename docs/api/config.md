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
  "last_checked_at": "ISO8601|null",
  "latest_version": "string|null",
  "update_available": boolean,
  "check_enabled": boolean,
  "check_interval_hours": integer
}
```

## POST /config/updates/check
Manually trigger an update check. Admin only.

Always performs a real check against GitHub — bypasses both the interval throttle and in-memory version cache regardless of when the last check ran.

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
