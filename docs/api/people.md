# People

## Person Object

```json
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
```

---

## GET /people
List all people.

**Response (200):** Array of person objects

## POST /people
Create new person. Admin only.

**Request:**
```json
{
  "name": "string",
  "username": "string",
  "password": "string|null"
}
```

**Response (201):** Created person

## PUT /people/{username}
Update person settings. Admin or self only.

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

## DELETE /people/{username}
Delete person. Admin only — cannot delete self.

**Response (204):** No content

## POST /people/{person_id}/redeem
Redeem points for a person. Admin only. Deducts points from person's total.

**Request:**
```json
{
  "amount": integer,
  "reason": "string"
}
```

**Response (200):** Updated person with reduced points  
**Response (400):** Invalid amount or insufficient points  
**Response (404):** Person not found

## GET /people/{person_id}/redemptions
Get redemption history for a person.

**Response (200):**
```json
[
  {
    "id": integer,
    "person_id": integer,
    "amount": integer,
    "reason": "string",
    "timestamp": "ISO8601"
  }
]
```
