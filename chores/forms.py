from django import forms
from django.utils import timezone

from .models import Chore


class QuickAddForm(forms.Form):
    name = forms.CharField(max_length=120, strip=True)


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["name", "recurrence_type", "weekly_target", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

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

    def clean_completed_on(self):
        return self.cleaned_data["completed_on"] or timezone.localdate()
