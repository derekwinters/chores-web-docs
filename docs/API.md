# Chores API Documentation

## Overview

REST API for managing household chores, assignments, and tracking. Built with FastAPI.

**Base URL:** `/api`  
**Authentication:** Bearer token (JWT)  
**Default Port:** 8000

## Authentication

All endpoints except `/auth/setup-status` require Bearer token authentication.

```
Authorization: Bearer <access_token>
```

### Auth Endpoints

#### POST /auth/login
Login with username and password.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "username": "string",
    "is_admin": boolean
  }
}
```

#### GET /auth/setup-status
Check if system is initialized (no users exist).

**Response (200):**
```json
{
  "is_setup": boolean
}
```

#### POST /auth/logout
Logout and invalidate current token.

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

#### PUT /auth/password
Change password for current user.

**Request:**
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

---

## Chores

### GET /chores
List all chores.

**Query Parameters:** None

**Response (200):**
```json
[
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
]
```

### GET /chores/{chore_id}
Get single chore by unique_id.

**Response (200):** Same as list item above  
**Response (404):** Chore not found

### POST /chores
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

**Schedule Config Examples:**

Weekly:
```json
{
  "days": [0, 2, 5],
  "every_other_week": false
}
```

Monthly (by date):
```json
{
  "day_of_month": 15
}
```

Monthly (by weekday):
```json
{
  "weekday_occurrence": {
    "week": 1,
    "weekday": 0
  }
}
```

Interval:
```json
{
  "days": 7
}
```

With conditions:
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

**Response (201):** Created chore with computed fields

### PUT /chores/{chore_id}
Update chore.

**Request:** Same fields as POST (all optional)

**Response (200):** Updated chore

### DELETE /chores/{chore_id}
Delete chore and all associated points history.

**Response (204):** No content

### POST /chores/{chore_id}/complete
Mark chore as completed by a person, award points.

**Request:**
```json
{
  "completed_by": "string|null"
}
```

**Response (200):** Updated chore

### POST /chores/{chore_id}/skip
Skip chore (no points awarded), calculate next due date.

**Response (200):** Updated chore

### POST /chores/{chore_id}/skip-reassign
Skip and reassign to another person.

**Request:**
```json
{
  "assignee": "string|null"
}
```

**Response (200):** Updated chore

### POST /chores/{chore_id}/reassign
Reassign chore to different person.

**Request:**
```json
{
  "assignee": "string"
}
```

**Response (200):** Updated chore

### POST /chores/{chore_id}/mark-due
Manually mark chore as due (skip to next cycle).

**Response (200):** Updated chore

---

## People

### GET /people
List all people.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "string",
    "username": "string",
    "is_admin": boolean,
    "color": "#RRGGBB",
    "goal_7d": integer,
    "goal_30d": integer,
    "preferred_theme": "string|null"
  }
]
```

### POST /people
Create new person (admin only).

**Request:**
```json
{
  "name": "string",
  "username": "string",
  "password": "string|null"
}
```

**Response (201):** Created person

### PUT /people/{username}
Update person settings (admin or self only).

**Request:**
```json
{
  "color": "#RRGGBB|null",
  "goal_7d": integer|null,
  "goal_30d": integer|null,
  "preferred_theme": "string|null"
}
```

**Response (200):** Updated person

### DELETE /people/{username}
Delete person (admin only, cannot delete self).

**Response (204):** No content

---

## Points

### GET /points
Get leaderboard (points in last 30 days).

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

### GET /points/summary
Get summary stats for all people.

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

### GET /points/{person}
Get points history for specific person.

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

### GET /points/stats/{person}
Get stats for specific person (current period).

**Response (200):**
```json
{
  "person": "string",
  "points_7d": integer,
  "points_30d": integer
}
```

---

## Log

### GET /log
Get chore action log with optional filters.

**Query Parameters:**
- `person`: Filter by person (string)
- `chore_id`: Filter by chore (string)
- `action`: Filter by action type (completed|skipped|reassigned|marked_due|marked_due_by_schedule)
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

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

---

## Themes

### GET /theme/list
List all themes (default + custom).

**Response (200):**
```json
[
  {
    "id": "string",
    "name": "string",
    "colors": {
      "bg": "#RRGGBB",
      "surface": "#RRGGBB",
      "accent": "#RRGGBB",
      "success": "#RRGGBB",
      "warning": "#RRGGBB",
      "danger": "#RRGGBB"
    }
  }
]
```

### GET /theme/current
Get current user's preferred theme.

**Response (200):** Theme object (see above)

### POST /theme/set/{theme_id}
Set current user's preferred theme.

**Response (200):** Theme object

### POST /theme/save
Create new custom theme.

**Request:**
```json
{
  "name": "string",
  "colors": {
    "bg": "#RRGGBB",
    "surface": "#RRGGBB",
    "accent": "#RRGGBB",
    "success": "#RRGGBB",
    "warning": "#RRGGBB",
    "danger": "#RRGGBB"
  }
}
```

**Response (200):** Created theme

### DELETE /theme/delete/{theme_id}
Delete custom theme (cannot delete defaults).

**Response (204):** No content  
**Response (400):** Cannot delete default theme

---

## Config

### GET /config
Get system configuration.

**Response (200):**
```json
{
  "admin_theme": "string"
}
```

### PUT /config
Update system configuration (admin only).

**Request:**
```json
{
  "admin_theme": "string|null"
}
```

**Response (200):** Updated config

---

## Health

### GET /health
Health check endpoint.

**Response (200):**
```json
{
  "status": "ok"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "string"
}
```

**Common Status Codes:**
- 200: Success
- 201: Created
- 204: No content (delete)
- 400: Bad request (validation error)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not found
- 500: Internal server error
