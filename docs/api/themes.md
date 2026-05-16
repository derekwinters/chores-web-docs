# Themes

## 9-Color Theme System

All themes use a unified 9-color palette for consistent styling across the application.

## Theme Object

```json
{
  "id": "string",
  "name": "string",
  "colors": {
    "bg": "#RRGGBB",
    "surface": "#RRGGBB",
    "surface2": "#RRGGBB",
    "accent": "#RRGGBB",
    "primary": "#RRGGBB",
    "secondary": "#RRGGBB",
    "success": "#RRGGBB",
    "warning": "#RRGGBB",
    "error": "#RRGGBB"
  }
}
```

### Color Definitions

| Color | Purpose |
|-------|---------|
| `bg` | Page background |
| `surface` | Card/panel background (layer 1) |
| `surface2` | Elevated surface (layer 2), inputs, tags |
| `accent` | Highlights, links, focus rings, active borders |
| `primary` | Primary buttons and interactive controls |
| `secondary` | Secondary buttons, lower-emphasis controls |
| `success` | Positive states, completion indicators |
| `warning` | Caution states, due-soon indicators |
| `error` | Destructive actions, validation errors (renamed from `danger`) |

---

## GET /theme/list
List all themes — defaults and custom.

**Response (200):** Array of theme objects

## GET /theme/current
Get current user's preferred theme (personal preference or site default).

**Response (200):**
```json
{
  "id": "string",
  "name": "string",
  "colors": { ... },
  "is_personal": boolean
}
```

## GET /theme/default-info
Get current site-wide default theme name and ID. Accessible to all authenticated users.

**Response (200):**
```json
{
  "id": "string",
  "name": "string"
}
```

## GET /theme/default
Get complete site-wide default theme (admin only).

**Response (200):** Theme object  
**Response (403):** Forbidden — not admin

## POST /theme/set/{theme_id}
Set personal theme preference for current user.

**Response (200):** Theme object

## DELETE /theme/personal
Clear personal theme preference so user inherits site default.

**Response (204):** No content

## PUT /theme/default/{theme_id}
Set site-wide default theme (admin only).

**Response (200):** Theme object  
**Response (404):** Theme not found  
**Response (403):** Forbidden — not admin

## POST /theme/save
Create new custom theme.

**Request:**
```json
{
  "name": "string",
  "colors": {
    "bg": "#RRGGBB",
    "surface": "#RRGGBB",
    "surface2": "#RRGGBB",
    "accent": "#RRGGBB",
    "primary": "#RRGGBB",
    "secondary": "#RRGGBB",
    "success": "#RRGGBB",
    "warning": "#RRGGBB",
    "error": "#RRGGBB"
  }
}
```

**Response (200):** Created theme with assigned ID

## PATCH /theme/update/{theme_id}
Update custom theme (name and/or colors). Cannot modify default themes.

**Request:**
```json
{
  "name": "string (optional)",
  "colors": { ... } (optional, all 9 fields required if provided)
}
```

**Response (200):** Updated theme  
**Response (400):** Cannot modify default themes  
**Response (404):** Theme not found

## PATCH /theme/rename/{theme_id}
Rename custom theme. Cannot modify default themes.

**Request:**
```json
{
  "name": "string"
}
```

**Response (200):** Updated theme  
**Response (400):** Cannot modify default themes or name is required  
**Response (404):** Theme not found

## DELETE /theme/delete/{theme_id}
Delete custom theme. Cannot delete defaults.

**Response (200):**
```json
{
  "message": "Theme deleted"
}
```

**Response (400):** Cannot delete default theme  
**Response (404):** Theme not found
