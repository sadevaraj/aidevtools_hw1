# Shared Chore Tracker (2-Person) — Spec & Plan

## Problem

Homework 1 starts from a deliberately vague idea: *"a tool for managing shared household
chores."* This project narrows the scope to a **2-person shared household chore
tracker**: two members, recurring chores, a due-today view, and streak visibility.

## Approach

A small Django web app on the default SQLite database. One flat list of chores, each with
an assignee and recurrence rule. The app surfaces what's due, lets either member tick
things off with one click, and tracks streaks.

## Settled scope

**Core features**

1. **Recurring chores** — three kinds:
   - *Daily* — e.g. physical exercise, due every day.
   - *Flexible weekly target* — e.g. "self-learning 2× this week", done on any days.
   - *One-off* — a single task with a due date, no repetition.
2. **Two household members** — chores are assigned to one of two people, and completions
   record who did them.
3. **In-app reminders** — a "Today" view listing what's due, with overdue items
   highlighted. No email, no push, no desktop notifications.
4. **History & streaks** — current streak and total completion count per chore.
5. **Quick-add** — type a name, press Enter, chore exists.

**Out of scope**

- More than two users, login/authentication, or multi-household support
- Categories, tags, priorities, colour coding
- Notes, links, or descriptions on chores
- Calendar/month view
- Email, push, or desktop notifications
- Deployment and hosted databases

## Decisions

| Question | Decision |
| --- | --- |
| Users | Exactly 2 household members, no auth |
| Form factor | Django web app |
| Grouping | Flat list, no categories |
| Chore detail | Name only — no notes or links |
| Recurrence | Daily, flexible N-per-week, or one-off |
| Reminders | In-app only |
| History | Current streak + completion count per chore |
| Streak rule | One grace period allowed before a streak resets |
| Backdating | Allowed — can log a completion for an earlier day |
| Retirement | Archive (history kept), not delete |
| Quick-add | Name + Enter creates a chore |
| Database | Default SQLite, local file |
| Hosting | Local only, `runserver` |

## Data model (draft)

**Chore**
- `name` — text
- `assigned_to` — FK to household member
- `recurrence_type` — `daily` | `weekly_target` | `one_off`
- `weekly_target` — int, only meaningful when type is `weekly_target`
- `due_date` — date, only meaningful when type is `one_off`
- `is_archived` — bool
- `created_at`

**HouseholdMember**
- `name` — text
- `is_active` — bool
- `created_at`

**Completion**
- `chore` — FK
- `completed_on` — date (defaults to today, editable for backdating)
- `completed_by` — FK to household member
- `created_at`

Streaks and "due today" are **derived** from `Completion` rows, not stored. That means no
scheduled job, no nightly task, and nothing that can drift out of sync. It also means the
derivation logic is the heart of the app.

### Streak semantics

- *Daily chore* — streak counts consecutive days with a completion. **One** missed day is
  forgiven; a second consecutive miss resets to 0.
- *Weekly-target chore* — streak counts consecutive weeks where completions met or beat
  the target, with the same one-period grace.
- *One-off* — no streak; it's simply done or not.

## Todos

1. Add `.gitignore`, `README.md`, and `_docs/plan.md` to the repo. Commit and push.
2. Set up Django with `uv`; create the project and app, register the app in
   `INSTALLED_APPS` in `settings.py`.
3. Define the `Chore` and `Completion` models; make and run migrations.
4. Build chore management — quick-add, edit, archive.
5. Build the Today dashboard — due today, overdue highlighting, weekly progress.
6. Implement mark-done and undo, including backdating to an earlier day.
7. Implement streak and completion-count logic with the grace-period rule.
8. Write `backlog.md` from this plan (homework Question 4).
9. Cover streak logic and due-today logic with Django tests.

## Notes

- Homework answers to note while working: the app is registered in `settings.py`; the
  server starts with `uv run python manage.py runserver`; tests run with
  `uv run python manage.py test`.
- Environment is ready: Python 3.12.3, SQLite 3.45.1 (bundled with Python), `uv`
  installed. Nothing extra to install beyond Django itself.
- Streak logic is the subtlest part of the app and deserves the heaviest test coverage —
  especially the grace-period boundary, where off-by-one errors hide.
- Deferred, not rejected: if this ever gets deployed for phone use, the local SQLite file
  won't survive redeploys and a hosted Postgres (Neon) becomes worth the swap.
