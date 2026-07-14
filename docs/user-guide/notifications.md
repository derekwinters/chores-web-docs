# Notifications

Chores Web keeps you on top of your responsibilities with notifications. When a
chore becomes due, the app lets you know — in the web app through an in-app bell
and toast, and on Android through a system notification. This page explains what
triggers a notification, how notifications are delivered and cleared, and how to
control which ones you receive.

---

## What Triggers a Notification

### Chore-Due Events

The current version supports a single kind of notification: **chore due**.

- When a chore becomes due, Chores Web generates one notification for each
  person the chore is relevant to (the assignee for a fixed or rotating chore,
  or everyone eligible for an open chore).
- The moment a chore is considered "due" is controlled by the household's
  **due time hour** setting — the hour of day when scheduled chores transition
  to due/overdue. See [Admin Features](admin.md) for how admins configure this.
- You only get a notification for a chore that is actually relevant to you — you
  will not be notified about chores assigned to someone else.

---

## How Notifications Are Delivered and Cleared

The server owns the state of every notification, so your notifications stay
consistent across the web app and the Android app.

### Delivery

- A notification is **delivered** the first time a client fetches it. The server
  records the delivery time at that point, so a given notification is only ever
  "new" once, no matter which device sees it first.

### Acknowledgement

- **Acknowledging** a notification marks it as handled. Acknowledge a
  notification once you have seen it and no longer need to be reminded.
- Acknowledgement is shared across devices — acknowledge on the web and it is
  acknowledged on Android too.

### Automatic (stale) dismissal

You do not have to clean up old notifications yourself. The server dismisses
notifications automatically:

- If a chore-due notification is never acknowledged and its chore is no longer
  due (for example, someone completed or skipped the chore), the server marks
  the notification **dismissed** — it disappears without you having to do
  anything.
- A notification that becomes stale *before* it is ever delivered is never shown
  at all. This means you won't be greeted by a pile of notifications for chores
  that were already handled while you were away.

!!! note
    Because dismissal is automatic and server-side, there is nothing to purge or
    reset manually. Acknowledge the notifications you have acted on, and let the
    server clear the rest.

---

## In the Web App

### The Notification Bell

- A **bell icon** sits in the top navigation bar.
- An **unread badge** on the bell shows how many notifications you have not yet
  acknowledged.
- When a new notification arrives, a **toast** briefly appears so you notice it
  without having to open the bell.

### The Notification Log

1. Click the **bell** (or navigate to **Notifications**) to open the log view.
2. The log lists your notifications, newest first, with each chore-due item
   showing what is due.
3. Click **Acknowledge** on an item once you have dealt with it. Acknowledged
   items clear from your unread count.

---

## On Android

The Android app surfaces the same notifications as system notifications in your
device's notification tray.

### Background Polling

- The Android app checks the server for new notifications on a schedule, in the
  background, using Android's built-in **WorkManager**.
- When it finds new notifications, it posts them as **system notifications** —
  the standard Android notifications that appear in your tray and on your lock
  screen.
- There is **no push/FCM** involved: notifications are pulled by the app on its
  polling schedule rather than pushed instantly from a server. A brand-new
  chore-due notification appears at the next poll, not necessarily the instant
  it is generated.

### Configurable Poll Interval

- The polling frequency is configurable in the Android app's **Settings**
  screen. A shorter interval means more timely notifications; a longer interval
  is easier on battery and data.

### "Not Connected in X Days" Alert

- The Android app also raises a local alert if it has not managed to reach the
  server recently — the **"not connected in X days"** reminder.
- This is generated on the device itself (not by the server), so it can warn you
  even when connectivity is the very thing that is broken.
- The number of days before this alert fires is also configurable in the Android
  app's **Settings** screen.

---

## Notification Preferences

You can control which types of notification you receive.

- Preferences are **per type**. In the current version there is one type,
  **chore due**, which you can enable or disable.
- A type you have not explicitly changed is **enabled by default** — if you have
  never touched your notification preferences, you receive all notifications.
- Edit your preferences in the **web app's Settings** section or on the
  **Android app's Settings** screen. Your preferences apply to your account, so
  they take effect on every device you sign in to.

!!! tip
    Disabling the **chore due** type stops new chore-due notifications from being
    generated for you. Re-enable it at any time from either client's settings.
