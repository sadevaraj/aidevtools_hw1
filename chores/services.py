from dataclasses import dataclass
from datetime import date, timedelta

from django.utils import timezone

from .models import Chore


@dataclass(frozen=True)
class TodayStatus:
    is_due: bool
    is_overdue: bool
    weekly_progress: int | None = None


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def get_today_status(chore: Chore, *, today: date | None = None) -> TodayStatus:
    current_day = today or timezone.localdate()
    if chore.recurrence_type == Chore.RecurrenceType.DAILY:
        done_today = chore.completions.filter(completed_on=current_day).exists()
        return TodayStatus(is_due=not done_today, is_overdue=False)

    if chore.recurrence_type == Chore.RecurrenceType.WEEKLY_TARGET:
        start = week_start(current_day)
        end = start + timedelta(days=6)
        week_count = chore.completions.filter(completed_on__range=(start, end)).count()
        return TodayStatus(
            is_due=week_count < (chore.weekly_target or 0),
            is_overdue=False,
            weekly_progress=week_count,
        )

    has_completion = chore.completions.exists()
    if has_completion:
        return TodayStatus(is_due=False, is_overdue=False)

    is_due = chore.due_date is not None and chore.due_date <= current_day
    is_overdue = chore.due_date is not None and chore.due_date < current_day
    return TodayStatus(is_due=is_due, is_overdue=is_overdue)


def get_completion_count(chore: Chore) -> int:
    return chore.completions.count()


def get_current_streak(chore: Chore, *, today: date | None = None) -> int:
    current_day = today or timezone.localdate()
    if chore.recurrence_type == Chore.RecurrenceType.ONE_OFF:
        return 0

    if chore.recurrence_type == Chore.RecurrenceType.DAILY:
        completion_days = set(chore.completions.values_list("completed_on", flat=True))
        if not completion_days:
            return 0
        streak = 0
        grace_used = False
        cursor = current_day
        while True:
            if cursor in completion_days:
                streak += 1
            elif not grace_used:
                grace_used = True
            else:
                break
            cursor -= timedelta(days=1)
        return streak

    target = chore.weekly_target or 0
    if target < 1:
        return 0

    weekly_counts: dict[date, int] = {}
    for completed_on in chore.completions.values_list("completed_on", flat=True):
        key = week_start(completed_on)
        weekly_counts[key] = weekly_counts.get(key, 0) + 1

    weeks_met = {week: count >= target for week, count in weekly_counts.items()}
    if not weeks_met:
        return 0

    streak = 0
    grace_used = False
    cursor = week_start(current_day)
    while True:
        met = weeks_met.get(cursor, False)
        if met:
            streak += 1
        elif not grace_used:
            grace_used = True
        else:
            break
        cursor -= timedelta(days=7)
    return streak
