from django import forms
from django.utils import timezone

from .models import Chore, HouseholdMember


class QuickAddForm(forms.Form):
    name = forms.CharField(max_length=120, strip=True)
    assigned_to = forms.ModelChoiceField(queryset=HouseholdMember.objects.none())

    def __init__(self, *args, members_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = members_queryset or HouseholdMember.objects.filter(is_active=True)


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["name", "assigned_to", "recurrence_type", "weekly_target", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, members_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = members_queryset or HouseholdMember.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        recurrence_type = cleaned_data.get("recurrence_type")
        if recurrence_type != Chore.RecurrenceType.WEEKLY_TARGET:
            cleaned_data["weekly_target"] = None
        if recurrence_type != Chore.RecurrenceType.ONE_OFF:
            cleaned_data["due_date"] = None
        return cleaned_data


class CompletionForm(forms.Form):
    completed_on = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    completed_by = forms.ModelChoiceField(queryset=HouseholdMember.objects.none())

    def __init__(self, *args, members_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["completed_by"].queryset = members_queryset or HouseholdMember.objects.filter(is_active=True)

    def clean_completed_on(self):
        return self.cleaned_data["completed_on"] or timezone.localdate()
