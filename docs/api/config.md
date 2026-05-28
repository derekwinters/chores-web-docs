# Config & Health

## GET /config
Get system configuration.

**Response (200):**
```json
{
  "title": "string",
  "auth_enabled": true,
  "timezone": "string",
  "due_soon_days": 3,
  "due_time_hour": 6,
  "update_check_enabled": true,
  "update_check_interval": 24
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | `"Family Chores"` | App display title |
| `auth_enabled` | boolean | `true` | Whether authentication is required |
| `timezone` | string | `"UTC"` | IANA timezone for scheduling (e.g. `"America/New_York"`) |
| `due_soon_days` | integer | `3` | Days in advance to mark chores as due soon (1–365) |
| `due_time_hour` | integer | `6` | Hour of day (0–23) when the scheduler marks overdue chores as due |
| `update_check_enabled` | boolean | `true` | Whether automatic update checks are enabled |
| `update_check_interval` | integer | `24` | Interval in hours between automatic update checks |

## PUT /config
Update system configuration. Admin only.

**Request:**
```json
{
  "title": "string|null",
  "auth_enabled": "boolean|null",
  "timezone": "string|null",
  "due_soon_days": "integer|null",
  "due_time_hour": "integer|null",
  "update_check_enabled": "boolean|null",
  "update_check_interval": "integer|null"
}
```

All fields are optional. Only provided fields are updated.

| Field | Validation | Notes |
|-------|-----------|-------|
| `due_soon_days` | 1–365 | Returns 422 if out of range |
| `due_time_hour` | 0–23 | Returns 422 if out of range; reschedules the overdue-chore transition job immediately on save |
| `timezone` | IANA string | Reschedules the overdue-chore transition job immediately on save |

**Response (200):** Updated config (same shape as GET /config)

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
