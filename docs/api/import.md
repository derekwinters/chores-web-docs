# Import

Import previously exported configuration data to restore or migrate settings.

## POST /import/config
Import configuration data (people, chores, settings) from backup.

**Authentication:** Required (Bearer token)

**Request:**
```json
{
  "people": [
    {
      "name": "string",
      "username": "string",
      "color": "#RRGGBB",
      "goal_7d": integer,
      "goal_30d": integer,
      "preferred_theme": "string|null"
    }
  ],
  "chores": [
    {
      "unique_id": "string",
      "name": "string",
      "schedule_type": "weekly|monthly|interval",
      "schedule_config": {},
      "assignment_type": "open|rotating|fixed",
      "eligible_people": ["string"],
      "assignee": "string|null",
      "points": integer,
      "disabled": boolean
    }
  ],
  "settings": [
    {
      "key": "string",
      "value": "string"
    }
  ]
}
```

**Response (200):**
```json
{
  "message": "Import successful",
  "counts": {
    "people_imported": integer,
    "chores_imported": integer,
    "settings_imported": integer
  }
}
```

**Response (400):** Bad request / validation error
```json
{
  "detail": "string"
}
```

**Response (401):** Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

**Notes:**
- **DESTRUCTIVE:** Replaces all existing data (people, chores, settings)
- Only authenticated users can import
- File should match export format from GET /export/config
- Validates all required fields before import
- On failure, original data is preserved
- Does not import history logs (PointsLog, ChoreLog) — these are not included in exports
- Recommended to backup before importing

**Example Use Case:**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d @backup.json \
  http://localhost:8000/api/import/config
```

**Warning:**
This operation is destructive. Always backup your data before importing. Test imports in a development environment first.
