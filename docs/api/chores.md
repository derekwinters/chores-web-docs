# Chores

## Chore Object

```json
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
  "state": "due|complete",
  "disabled": boolean,
  "next_due": "YYYY-MM-DD|null",
  "current_assignee": "string|null",
  "age": integer|null,
  "schedule_summary": "string",
  "next_assignee": "string|null"
}
```

## Schedule Config

### Weekly
```json
{
  "days": [0, 2, 5],
  "every_other_week": false
}
```

### Monthly (by date)
```json
{
  "day_of_month": 15
}
```

### Monthly (by weekday)
```json
{
  "weekday_occurrence": {
    "week": 1,
    "weekday": 0
  }
}
```

### Interval
```json
{
  "days": 7
}
```

### With Conditions
```json
{
  "days": [0, 1, 2],
  "conditions": [
    { "type": "even_days" },
    { "type": "odd_days" },
    { "type": "weekdays", "days": [1, 2, 3] }
  ],
  "condition_failure": "skip"
}
```

---

## GET /chores
List all chores.

**Response (200):** Array of chore objects

## GET /chores/{chore_id}
Get single chore by `unique_id`.

**Response (200):** Chore object  
**Response (404):** Not found

## POST /chores
Create new chore.

**Request:**
```json
{
  "name": "string",
  "schedule_type": "weekly|monthly|interval",
  "schedule_config": {},
  "assignment_type": "open|rotating|fixed",
  "eligible_people": ["string"],
  "assignee": "string|null",
  "points": integer,
  "disabled": boolean
}
```

**Response (201):** Created chore with computed fields

## PUT /chores/{chore_id}
Update chore. All fields optional.

**Response (200):** Updated chore

## DELETE /chores/{chore_id}
Delete chore and all associated points history.

**Response (204):** No content

---

## POST /chores/{chore_id}/complete
Mark chore completed, award points.

**Request:**
```json
{
  "completed_by": "string|null"
}
```

**Response (200):** Updated chore

## POST /chores/{chore_id}/skip
Skip chore (no points), calculate next due date.

**Response (200):** Updated chore

## POST /chores/{chore_id}/skip-reassign
Skip and reassign to another person.

**Request:**
```json
{
  "assignee": "string|null"
}
```

**Response (200):** Updated chore

## POST /chores/{chore_id}/reassign
Reassign chore to different person.

**Request:**
```json
{
  "assignee": "string"
}
```

**Response (200):** Updated chore

## POST /chores/{chore_id}/mark-due
Manually mark chore as due (skip to next cycle).

**Response (200):** Updated chore
