from django.contrib import admin

from .models import Chore, Completion, HouseholdMember


@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("name", "assigned_to", "recurrence_type", "weekly_target", "due_date", "is_archived", "created_at")
    list_filter = ("assigned_to", "recurrence_type", "is_archived")
    search_fields = ("name", "assigned_to__name")


@admin.register(Completion)
class CompletionAdmin(admin.ModelAdmin):
    list_display = ("chore", "completed_by", "completed_on", "created_at")
    list_filter = ("completed_by", "completed_on")
    search_fields = ("chore__name", "completed_by__name")
