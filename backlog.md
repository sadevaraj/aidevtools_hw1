# Backlog — Personal Chore Tracker

Derived from [`_docs/plan.md`](_docs/plan.md).  
Scope: single-user Django app with recurring chores, today reminders, history/streaks, and quick-add.

## Task 1 — Define core data model and migrations

- Implement `Chore` and `Completion` models in the `chores` app.
- Add field validation rules:
  - `weekly_target` required and `>=1` when `recurrence_type=weekly_target`
  - `due_date` required when `recurrence_type=one_off`
- Create and apply migrations.
- Add Django admin registration for both models.

**Done when**
- `poetry run python manage.py makemigrations` creates migration files cleanly.
- `poetry run python manage.py migrate` applies successfully.
- Models are visible and editable in admin.

## Task 2 — Implement quick-add and chore list management

- Build a chores list page showing active chores.
- Add quick-add form (name + Enter) that creates a chore with sensible defaults.
- Add edit support for recurrence fields.
- Add archive action (soft-retire via `is_archived=True`).

**Done when**
- New chores can be created in one action from the list page.
- Archived chores no longer appear in active list.

## Task 3 — Build Today dashboard (due + overdue)

- Implement due logic for each recurrence type:
  - Daily: due each day unless already completed today.
  - Weekly target: due until target met for current week.
  - One-off: due on `due_date`, overdue after `due_date` if incomplete.
- Create Today view showing due chores and highlighting overdue ones.

**Done when**
- Today page correctly separates due and overdue items across all recurrence types.

## Task 4 — Add completion flows (done, undo, backdate)

- Implement mark-done action from Today/list.
- Support optional backdated completion date.
- Implement undo of a completion entry.

**Done when**
- Completion entries are created/removed correctly and UI reflects updated status immediately.

## Task 5 — Implement streak and completion history metrics

- Add derived metrics service/helpers:
  - `completion_count` per chore
  - `current_streak` for daily and weekly-target chores
- Apply grace-period rule (one missed period allowed; second miss resets).
- Show metrics in list/detail UI.

**Done when**
- Metrics are computed from `Completion` records only (not persisted counters).

## Task 6 — Add tests for business logic and key views

- Unit tests for due logic (daily/weekly-target/one-off).
- Unit tests for streak grace-period boundaries.
- Integration tests for quick-add and completion flows.

**Done when**
- `poetry run python manage.py test` passes with coverage over critical logic paths.
