from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Chore, Completion
from .services import get_current_streak, get_today_status, week_start


class ChoreModelValidationTests(TestCase):
    def test_weekly_target_chore_requires_min_target(self):
        chore = Chore(name="Learn", recurrence_type=Chore.RecurrenceType.WEEKLY_TARGET, weekly_target=0)
        with self.assertRaises(ValidationError):
            chore.full_clean()

    def test_one_off_requires_due_date(self):
        chore = Chore(name="Pay bill", recurrence_type=Chore.RecurrenceType.ONE_OFF)
        with self.assertRaises(ValidationError):
            chore.full_clean()

    def test_daily_chore_is_valid_without_optional_fields(self):
        chore = Chore(name="Exercise", recurrence_type=Chore.RecurrenceType.DAILY)
        chore.full_clean()


class TodayStatusTests(TestCase):
    def test_daily_due_if_not_completed_today(self):
        chore = Chore.objects.create(name="Exercise", recurrence_type=Chore.RecurrenceType.DAILY)
        status = get_today_status(chore, today=date(2026, 9, 7))
        self.assertTrue(status.is_due)

    def test_weekly_target_due_until_target_reached(self):
        today = date(2026, 9, 9)
        chore = Chore.objects.create(
            name="Study",
            recurrence_type=Chore.RecurrenceType.WEEKLY_TARGET,
            weekly_target=2,
        )
        Completion.objects.create(chore=chore, completed_on=today)
        status = get_today_status(chore, today=today)
        self.assertTrue(status.is_due)

        Completion.objects.create(chore=chore, completed_on=today - timedelta(days=1))
        status = get_today_status(chore, today=today)
        self.assertFalse(status.is_due)

    def test_one_off_becomes_overdue(self):
        today = date(2026, 9, 10)
        chore = Chore.objects.create(
            name="Renew card",
            recurrence_type=Chore.RecurrenceType.ONE_OFF,
            due_date=date(2026, 9, 8),
        )
        status = get_today_status(chore, today=today)
        self.assertTrue(status.is_due)
        self.assertTrue(status.is_overdue)


class StreakLogicTests(TestCase):
    def test_daily_streak_allows_one_grace_gap(self):
        today = date(2026, 9, 7)
        chore = Chore.objects.create(name="Exercise")
        Completion.objects.create(chore=chore, completed_on=today)
        Completion.objects.create(chore=chore, completed_on=today - timedelta(days=1))
        Completion.objects.create(chore=chore, completed_on=today - timedelta(days=3))
        self.assertEqual(get_current_streak(chore, today=today), 3)

    def test_daily_streak_resets_after_second_gap(self):
        today = date(2026, 9, 7)
        chore = Chore.objects.create(name="Exercise")
        Completion.objects.create(chore=chore, completed_on=today - timedelta(days=3))
        self.assertEqual(get_current_streak(chore, today=today), 0)

    def test_weekly_target_streak_allows_one_grace_week(self):
        today = date(2026, 9, 16)
        chore = Chore.objects.create(
            name="Study",
            recurrence_type=Chore.RecurrenceType.WEEKLY_TARGET,
            weekly_target=2,
        )
        current_week = week_start(today)
        older_week = current_week - timedelta(days=14)

        Completion.objects.create(chore=chore, completed_on=current_week)
        Completion.objects.create(chore=chore, completed_on=current_week + timedelta(days=1))
        Completion.objects.create(chore=chore, completed_on=older_week)
        Completion.objects.create(chore=chore, completed_on=older_week + timedelta(days=2))
        self.assertEqual(get_current_streak(chore, today=today), 2)

    def test_weekly_target_streak_resets_after_second_miss(self):
        today = date(2026, 9, 16)
        chore = Chore.objects.create(
            name="Study",
            recurrence_type=Chore.RecurrenceType.WEEKLY_TARGET,
            weekly_target=1,
        )
        old_week = week_start(today) - timedelta(days=14)
        Completion.objects.create(chore=chore, completed_on=old_week)
        self.assertEqual(get_current_streak(chore, today=today), 0)


class ChoreFlowTests(TestCase):
    def test_quick_add_creates_chore(self):
        response = self.client.post(reverse("chores:list"), {"name": "Laundry"})
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.get(name="Laundry")
        self.assertEqual(chore.recurrence_type, Chore.RecurrenceType.DAILY)

    def test_edit_and_archive_chore(self):
        chore = Chore.objects.create(name="Old name")
        edit_response = self.client.post(
            reverse("chores:edit", args=[chore.id]),
            {
                "name": "New name",
                "recurrence_type": Chore.RecurrenceType.ONE_OFF,
                "due_date": "2026-09-30",
                "weekly_target": "",
            },
        )
        self.assertEqual(edit_response.status_code, 302)
        chore.refresh_from_db()
        self.assertEqual(chore.name, "New name")
        self.assertEqual(chore.recurrence_type, Chore.RecurrenceType.ONE_OFF)

        archive_response = self.client.post(reverse("chores:archive", args=[chore.id]))
        self.assertEqual(archive_response.status_code, 302)
        chore.refresh_from_db()
        self.assertTrue(chore.is_archived)

    def test_mark_done_with_backdate_and_undo(self):
        chore = Chore.objects.create(name="Dishes")
        complete_response = self.client.post(
            reverse("chores:complete", args=[chore.id]),
            {"completed_on": "2026-09-01", "next": reverse("chores:list")},
        )
        self.assertEqual(complete_response.status_code, 302)
        completion = Completion.objects.get(chore=chore)
        self.assertEqual(str(completion.completed_on), "2026-09-01")

        undo_response = self.client.post(
            reverse("chores:undo", args=[completion.id]),
            {"next": reverse("chores:list")},
        )
        self.assertEqual(undo_response.status_code, 302)
        self.assertFalse(Completion.objects.filter(chore=chore).exists())

    def test_today_view_shows_overdue_one_off(self):
        Chore.objects.create(name="Archived", is_archived=True)
        Chore.objects.create(
            name="Renew card",
            recurrence_type=Chore.RecurrenceType.ONE_OFF,
            due_date=date.today() - timedelta(days=1),
        )
        response = self.client.get(reverse("chores:today"))
        self.assertContains(response, "Renew card")
        self.assertContains(response, "OVERDUE")
        self.assertNotContains(response, "Archived")
