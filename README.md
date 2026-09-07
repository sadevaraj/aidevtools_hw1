# Personal Chore Tracker

Homework 1 for the [DataTalksClub AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp).

The homework begins with a deliberately vague idea — *"a tool for managing shared
household chores"* — and asks you to turn it into a specification of your own. A
brainstorming session narrowed mine to something more personal: a **single-user chore
tracker** for recurring household and self-care tasks, in the spirit of TickTick.

No housemates, no rotation, no sharing. Just me, my chores, and whether I'm keeping up.

## Features

- **Recurring chores** — daily (e.g. exercise), a flexible weekly target (e.g. "learn
  something 2× this week"), or a one-off task with a due date.
- **In-app reminders** — a Today view showing what's due, with overdue items highlighted.
- **History and streaks** — current streak and total completion count per chore, with one
  grace period before a streak resets.
- **Quick-add** — type a name, press Enter, done.

The full specification, including data model and design decisions, is in
[`_docs/plan.md`](_docs/plan.md).

## Tech

Django with the default SQLite database, managed with
[Poetry](https://python-poetry.org/). The virtual environment is configured as
an in-project environment at `.venv/`.

## Getting started

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Then open http://127.0.0.1:8000/.

## Tests

```bash
poetry run python manage.py test
```

## Status

Early. The spec is settled and the backlog is being worked through — see
[`_docs/plan.md`](_docs/plan.md) for what's planned.
