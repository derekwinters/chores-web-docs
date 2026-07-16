# Admin Features & Settings

<!-- The images below are generated and committed by the "Documentation Screenshots"
     workflow (.github/workflows/screenshots.yml). Do not edit the block by hand —
     it is rewritten by scripts/wire_screenshots.py. -->
<!-- screenshots:auto:START -->
<!-- screenshots:auto:END -->

## Admin Features

### Managing Users

Admins can create, modify, and remove users:

**Create a user:**
1. Go to **Admin** → **Users**
2. Click **Add User**
3. Enter name, username, password
4. Set as admin (if needed)
5. Click **Create**

**Modify a user:**
1. Go to **Admin** → **Users**
2. Find the user, click **Edit**
3. Update name, goals, or theme preference
4. Click **Save**

**Delete a user:**
1. Go to **Admin** → **Users**
2. Find the user, click **Delete**
3. All their chores and history remain (for record)

### Editing Chores (Admin)

1. Go to **Chores**
2. Find the chore, click **Edit**
3. Modify name, schedule, points, assignment
4. Click **Save**

**Deleting a chore:**
1. Go to **Chores**
2. Find the chore, click **Delete**
3. Confirm the deletion (all history is kept)

### Export & Import Data

**Backup your data:**
1. Go to **Settings** → **Data Management**
2. Click **Export**
3. A JSON file downloads with all chores, people, settings
4. Save this file safely (Google Drive, cloud storage, etc.)

**Restore from backup:**
1. Go to **Settings** → **Data Management**
2. Click **Import**
3. Select your backup JSON file
4. Confirm (this replaces all current data)
5. Wait for import to complete

### System Settings

Admins can configure:
- Admin theme (applies to all users)
- System name/title (optional)
- Custom theme colors

### Notifications

Chores Web notifies each person when a chore becomes due (see the
[Notifications](notifications.md) guide for the full user-facing behavior).
The generation of these chore-due notifications is driven by the same
household schedule settings admins already manage:

- **`due_time_hour`** – the hour of day when scheduled chores transition to
  due/overdue. Chore-due notifications are generated at this transition, so
  changing `due_time_hour` also changes when people are notified.
- **`due_soon_days`** – the window used to consider a chore "due soon." Widening
  or narrowing this window changes which chores are surfaced as due, and
  therefore which ones generate notifications.

There is no separate notification schedule to configure — tuning these two
settings is how admins control notification timing.

**Stale notifications clean up themselves.** When a chore is completed, skipped,
or otherwise no longer due, any unacknowledged notification for it is dismissed
automatically by the server. Admins do not need to purge, reset, or otherwise
maintain a notification queue — there is no manual cleanup step.

### Unsaved Changes

Settings pages track unsaved changes:

- The **Save** button is grayed out when no changes have been made in that section.
- The **Save** button turns amber when there are unsaved changes.
- Navigating away from a settings page with unsaved changes triggers a confirmation prompt. Dismiss it to stay and save; confirm to discard your changes and leave.

This applies to all settings sections except Theme (which saves immediately on selection).

---

## Settings & Customization

### Personal Settings

1. Click your **avatar** (top-right) → **Settings**
2. Modify:
   - **7-Day Goal** – Weekly point target
   - **30-Day Goal** – Monthly point target
   - **Theme** – Light/dark mode or custom themes
3. Click **Save**

### Change Your Password

1. Click your **avatar** → **Settings**
2. Click **Change Password**
3. Enter old password, new password, confirm
4. Click **Update**

### Themes

**Available themes:**
- Light (default white/bright)
- Dark (dark background, white text)
- Custom (admin or user-created themes with custom colors)

To change theme:
1. Go to **Settings**
2. Select a theme from the dropdown
3. Apply immediately

### Logout

1. Click your **avatar** (top-right)
2. Click **Logout**
3. You're logged out, must login again to use the app
