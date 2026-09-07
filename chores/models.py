from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Chore(models.Model):
    class RecurrenceType(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY_TARGET = "weekly_target", "Weekly target"
        ONE_OFF = "one_off", "One-off"

    name = models.CharField(max_length=120)
    recurrence_type = models.CharField(
        max_length=20,
        choices=RecurrenceType.choices,
        default=RecurrenceType.DAILY,
    )
    weekly_target = models.PositiveSmallIntegerField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                name="weekly_target_required_for_weekly_target",
                condition=~Q(recurrence_type="weekly_target") | Q(weekly_target__gte=1),
            ),
            models.CheckConstraint(
                name="due_date_required_for_one_off",
                condition=~Q(recurrence_type="one_off") | Q(due_date__isnull=False),
            ),
        ]

    def clean(self):
        super().clean()
        if self.recurrence_type == self.RecurrenceType.WEEKLY_TARGET:
            if self.weekly_target is None or self.weekly_target < 1:
                raise ValidationError(
                    {"weekly_target": "Weekly target must be at least 1 for weekly_target chores."}
                )
        if self.recurrence_type == self.RecurrenceType.ONE_OFF and self.due_date is None:
            raise ValidationError({"due_date": "Due date is required for one_off chores."})

    def __str__(self):
        return self.name


class Completion(models.Model):
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE, related_name="completions")
    completed_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_on", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["chore", "completed_on"],
                name="unique_completion_per_chore_per_day",
            )
        ]

    def __str__(self):
        return f"{self.chore.name} on {self.completed_on}"
