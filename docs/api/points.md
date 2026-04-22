# Points

## GET /points
Leaderboard — points earned in last 30 days.

**Response (200):**
```json
[
  {
    "person": "string",
    "points_7d": integer,
    "points_30d": integer
  }
]
```

## GET /points/summary
Summary stats for all people.

**Response (200):** Same as `/points`

## GET /points/{person}
Full points history for a specific person.

**Response (200):**
```json
[
  {
    "person": "string",
    "points": integer,
    "chore_id": "string",
    "completed_at": "ISO8601"
  }
]
```

## GET /points/stats/{person}
Aggregated stats for a specific person.

**Response (200):**
```json
{
  "person": "string",
  "points_7d": integer,
  "points_30d": integer
}
```
