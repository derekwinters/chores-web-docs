# Log

## GET /log
Chore action log with optional filters.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `person` | string | Filter by person |
| `chore_id` | string | Filter by chore |
| `action` | string | `completed`, `skipped`, `reassigned`, `marked_due`, `marked_due_by_schedule` |
| `start_date` | YYYY-MM-DD | Filter from date |
| `end_date` | YYYY-MM-DD | Filter to date |

**Response (200):**
```json
[
  {
    "id": 1,
    "chore_id": "string",
    "chore_name": "string",
    "person": "string",
    "action": "string",
    "timestamp": "ISO8601",
    "reassigned_to": "string|null"
  }
]
```
