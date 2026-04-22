# Themes

## Theme Object

```json
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
```

---

## GET /theme/list
List all themes — defaults and custom.

**Response (200):** Array of theme objects

## GET /theme/current
Get current user's preferred theme.

**Response (200):** Theme object

## POST /theme/set/{theme_id}
Set current user's preferred theme.

**Response (200):** Theme object

## POST /theme/save
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

## DELETE /theme/delete/{theme_id}
Delete custom theme. Cannot delete defaults.

**Response (204):** No content  
**Response (400):** Cannot delete default theme
