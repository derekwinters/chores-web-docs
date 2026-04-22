# API Reference

REST API for managing household chores, assignments, and tracking. Built with FastAPI.

**Base URL:** `/api`  
**Authentication:** Bearer token (JWT)  
**Default Port:** 8000  
**Interactive Docs:** `http://localhost:8000/docs`

## Authentication

All endpoints except `/auth/setup-status` require Bearer token authentication.

```
Authorization: Bearer <access_token>
```

### POST /auth/login
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

### GET /auth/setup-status
Check if system is initialized (no users exist).

**Response (200):**
```json
{
  "is_setup": boolean
}
```

### POST /auth/logout
Logout and invalidate current token.

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

### PUT /auth/password
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

## Error Responses

All errors follow this format:

```json
{
  "detail": "string"
}
```

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No content (delete) |
| 400 | Bad request / validation error |
| 401 | Unauthorized — missing or invalid token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not found |
| 500 | Internal server error |
