# Log

## GET /log
Chore action log with optional filters. Returns both chore actions (ChoreLog) and user management actions (UserLog).

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `person` | string | Filter by person (actor or affected person) |
| `chore_id` | string | Filter by chore ID. Use `0` for user management actions only. Omit for all logs. |
| `action` | string | Filter by single action type (see action list below) |
| `actions` | list[string] | Filter by multiple action types (comma-separated or multiple params) |
| `start_date` | YYYY-MM-DD | Filter from date (inclusive) |
| `end_date` | YYYY-MM-DD | Filter to date (inclusive) |

### Action Types

**Chore Actions:**
- `completed` — Chore marked complete
- `skipped` — Chore skipped
- `reassigned` — Chore reassigned to another person
- `marked_due` — Chore marked as due (manually)
- `marked_due_by_schedule` — Chore auto-marked due by schedule

**User Actions:**
- `person_created` — Person added
- `person_modified` — Person details updated
- `person_deleted` — Person removed

**Response (200):**
```json
[
  {
    "id": 1,
    "chore_id": "string|null",
    "chore_name": "string|null",
    "person": "string",
    "action": "string",
    "timestamp": "ISO8601",
    "reassigned_to": "string|null"
  }
]
```

## GET /log/retention
Get current log retention policy.

**Response (200):**
```json
{
  "retention_days": integer
}
```

Logs older than `retention_days` are automatically purged.

## POST /log/retention
Update log retention policy. Admin only.

**Request:**
```json
{
  "retention_days": integer
}
```

**Response (200):**
```json
{
  "retention_days": integer
}
```
