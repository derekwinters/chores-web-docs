# User Guide

Welcome to Chores Web! This guide will help you get started and make the most of the app.

## What is Chores Web?

Chores Web is a household chore management app that helps families and roommates organize, assign, and track responsibilities fairly. It supports flexible scheduling, point-based rewards, and keeps a complete audit log of all activities.

### Who Can Use This App?

- **Families** managing household chores across multiple members
- **Roommate groups** sharing apartment or house responsibilities
- **Anyone** wanting a fair, transparent way to distribute and track tasks

### Key Features

- Schedule chores by week, month, or custom intervals
- Assign chores as open (anyone), rotating (fair rotation), or fixed (specific person)
- Award points for completed chores and track progress
- View complete history of all chore actions
- Customize appearance with personal themes
- Backup and restore your data

---

## Getting Started

### Logging In

1. Open the app in your browser (provided URL from admin)
2. Enter your **username** and **password**
3. Click **Login**
4. You'll see the **Dashboard** with an overview of your chores and points

### Dashboard Overview

The main dashboard shows:
- **Your Points** – Total points earned, 7-day and 30-day goals
- **Chores Due** – Chores assigned to you or open for anyone
- **Quick Actions** – Complete or skip chores
- **Leaderboard** – Points ranking for all household members

### Navigation

Use the menu (top-left) to access:
- **Dashboard** – Home page and overview
- **Chores** – View and manage all chores
- **Points** – Detailed points history and goals
- **Log** – Complete audit trail of all actions
- **Settings** – Your personal preferences
- **Admin** (admin only) – Manage users and system settings

---

## Managing Chores

### View All Chores

1. Click **Chores** in the menu
2. See all household chores with their:
   - Name and description
   - Schedule (weekly, monthly, etc.)
   - Points awarded
   - Current state (due or complete)
   - Assigned person

### Complete a Chore

**For chores assigned to you:**
1. Find the chore in the list (or on Dashboard)
2. Click **Complete**
3. The chore is marked complete, you get the points!
4. Next occurrence is automatically scheduled

**For open chores (anyone can complete):**
1. Click the chore in the list
2. Click **Complete**
3. Chore is marked complete for you, points awarded

### Skip a Chore

If you can't complete a chore:
1. Click the chore in the list
2. Click **Skip**
3. Chore moves to next cycle without awarding points
4. The next assigned person (if rotating) takes it next cycle

### Reassign a Chore

If you need someone else to do the chore:
1. Click the chore
2. Click **Reassign**
3. Select the new person from the dropdown
4. Chore is reassigned, they'll see it next

### Creating Chores (Admin Only)

If you're an admin, you can create new chores:

1. Go to **Chores** → **Create New Chore**
2. Fill in:
   - **Name** – What is the chore? (e.g., "Vacuum Living Room")
   - **Schedule** – When does it repeat?
     - Weekly: Pick days (e.g., Monday, Wednesday, Friday)
     - Monthly: Pick date or weekday occurrence
     - Interval: Every N days
   - **Points** – How many points for completing? (default 1)
   - **Assignment Type** – How is it assigned?
     - **Open** – Anyone can complete it
     - **Rotating** – Cycles through eligible people
     - **Fixed** – Always the same person
   - **Eligible People** – Who can be assigned (for rotating/fixed)
3. Click **Create**

---

## Understanding Assignments

### Open Chores
- Anyone in the household can complete
- Whoever completes first gets the points
- Good for flexible tasks (take out trash, sweep kitchen)
- No specific assignment needed

### Rotating Chores
- Cycles through a list of people
- Each person does it when it's their turn
- Fair distribution over time
- Good for shared responsibility (mow lawn, clean bathroom)

Example: Lawn mowing rotates between Alex → Bailey → Charlie → Alex...

### Fixed Chores
- Same person always does it
- Never rotates
- Good for tasks needing specific skills or assigned to one person
- Can be reassigned if needed

---

## Points & Goal Tracking

### How Points Work

- **Earning:** You get points when you complete a chore
- **Amount:** Each chore awards a specific number of points (default 1)
- **Tracking:** Your total points are shown on the Dashboard
- **History:** See all point transactions in the **Points** page

**Example:**
- Vacuum (5 points) – complete, you get +5
- Dishes (2 points) – complete, you get +2
- Total: 7 points

### Goals

Set personal point goals to track progress:

**7-Day Goal:** Target points for the current week (Mon-Sun)
- Helps with weekly motivation
- Resets every Sunday

**30-Day Goal:** Target points for the current month
- Longer-term tracking
- Resets on the 1st of each month

### Checking Your Progress

1. Go to **Dashboard** or **Points** page
2. See your current points and goal progress
3. Compare with others on the leaderboard (if visible)

---

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
3. Update name, color, goals, or theme preference
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

---

## FAQ & Troubleshooting

### "I can't see a chore I'm supposed to do"

**Solutions:**
- Check **Dashboard** – it may not be due yet
- Go to **Chores** → look for chores with "Your Turn" or your name
- If rotating chore, your turn may not have started yet
- If fixed chore, admin may have assigned it to someone else
- Try refreshing the page (Ctrl+R or Cmd+R)

### "I completed the chore but didn't get points"

**Solutions:**
- Check **Points** page – the points should show up immediately
- If not there, try refreshing (Ctrl+R)
- If still missing, ask an admin – they can manually award points or check logs

### "The app logged me out unexpectedly"

**Solutions:**
- Log in again with your username and password
- Tokens expire after 1 year – if it's been that long, this is normal
- If you keep getting logged out quickly, ask admin (may be a connection issue)

### "I see an error message"

**Common errors:**
- "Network error" – Check internet connection
- "Unauthorized" – You may not have permission for that action
- "Not found" – The item may have been deleted
- Contact an admin if the error persists

### "Why can't I create/delete chores?"

- Only admins can create or delete chores
- Ask an admin for access or to create the chore for you

### "Can I change another person's password?"

- **No** – Only admins can reset passwords through the admin panel
- Ask an admin to reset your password if forgotten

### "How do I see who did what?"

- Go to **Log** to see all chore actions (completion, skip, reassign, etc.)
- Each entry shows who, what, when

### "Can I export my points history?"

- Export via **Settings** → **Data Management** includes your PointsLog
- The JSON file has all transactions with timestamps
- You can analyze it in Excel or a spreadsheet

---

## Settings & Customization

### Personal Settings

1. Click your **avatar** (top-right) → **Settings**
2. Modify:
   - **Color** – Your personal color on the dashboard
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

---

## Tips & Best Practices

### For Fair Rotation

- Use rotating chores for shared tasks
- Make sure "Eligible People" includes everyone who should take turns
- Check the rotation regularly to ensure fairness

### For Motivation

- Set realistic 7-day and 30-day goals
- Check leaderboard occasionally for friendly competition
- Celebrate reaching goals!

### For Household Efficiency

- Use fixed chores for specialized tasks (yard work, car washing)
- Use open chores for quick tasks (sweep, wipe counters)
- Use rotating for regular shared tasks (dishes, bathrooms)
- Adjust points to reflect difficulty (quick tasks = 1-2 pts, complex = 5+ pts)

### Troubleshooting Tips

- **Stuck?** Check the **Log** page to understand what's happening
- **Confused about a chore?** Click it to see full details, schedule, and history
- **Need help?** Ask your admin or check this guide again
- **Found a bug?** Report it to the development team

---

## Getting Help

- **Admin questions** – Contact your household admin
- **How-to questions** – Check this guide first
- **Technical issues** – Check the Troubleshooting section above
- **Feature requests** – Talk to your admin
