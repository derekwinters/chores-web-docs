# Export

Export system configuration data for backup and data transfer purposes.

## GET /export/config
Export all configuration data (people, chores, settings).

**Authentication:** Required (Bearer token)

**Response (200):**
```json
{
  "people": [
    {
      "id": 1,
      "name": "string",
      "username": "string",
      "is_admin": boolean,
      "color": "#RRGGBB",
      "goal_7d": integer,
      "goal_30d": integer,
      "points": integer,
      "preferred_theme": "string|null"
    }
  ],
  "chores": [
    {
      "id": 1,
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

**Notes:**
- Exports complete configuration data (all people, chores, settings)
- Does not include history logs (ChoreLog, PointsLog)
- Does not include computed/transient fields (next_due, current_assignee, age)
- Use for backups or data migration to another instance
- Any authenticated user can export

**Example Use Case:**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/export/config \
  > backup.json
```
