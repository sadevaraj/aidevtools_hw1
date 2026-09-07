from django.contrib import admin

from .models import Chore, Completion


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("name", "recurrence_type", "weekly_target", "due_date", "is_archived", "created_at")
    list_filter = ("recurrence_type", "is_archived")
    search_fields = ("name",)


@admin.register(Completion)
class CompletionAdmin(admin.ModelAdmin):
    list_display = ("chore", "completed_on", "created_at")
    list_filter = ("completed_on",)
    search_fields = ("chore__name",)
