from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import ChoreForm, CompletionForm, QuickAddForm
from .models import Chore, Completion
from .services import get_completion_count, get_current_streak, get_today_status


def _active_chores_queryset():
    return Chore.objects.filter(is_archived=False).prefetch_related(
        Prefetch("completions", queryset=Completion.objects.order_by("-completed_on", "-created_at"))
    )


def _chore_cards(chores, today):
    cards = []
    for chore in chores:
        cards.append(
            {
                "chore": chore,
                "status": get_today_status(chore, today=today),
                "completion_count": get_completion_count(chore),
                "current_streak": get_current_streak(chore, today=today),
            }
        )
    return cards


@require_http_methods(["GET", "POST"])
def chore_list(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    quick_add_form = QuickAddForm()

    response_status = 200
    if request.method == "POST":
        quick_add_form = QuickAddForm(request.POST)
        if quick_add_form.is_valid():
            Chore.objects.create(name=quick_add_form.cleaned_data["name"])
            return redirect("chores:list")
        response_status = 400

    chores = _active_chores_queryset()
    context = {
        "quick_add_form": quick_add_form,
        "chore_cards": _chore_cards(chores, today),
        "completion_form": CompletionForm(),
        "today": today,
    }
    return render(request, "chores/chore_list.html", context, status=response_status)


@require_http_methods(["GET", "POST"])
def chore_edit(request: HttpRequest, chore_id: int) -> HttpResponse:
    chore = get_object_or_404(Chore, pk=chore_id)
    response_status = 200
    if request.method == "POST":
        form = ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            form.save()
            return redirect("chores:list")
        response_status = 400
    else:
        form = ChoreForm(instance=chore)
    return render(request, "chores/chore_edit.html", {"form": form, "chore": chore}, status=response_status)


@require_http_methods(["POST"])
def chore_archive(request: HttpRequest, chore_id: int) -> HttpResponse:
    chore = get_object_or_404(Chore, pk=chore_id)
    chore.is_archived = True
    chore.save(update_fields=["is_archived"])
    return redirect("chores:list")


@require_http_methods(["GET"])
def today_dashboard(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    chores = _active_chores_queryset()
    cards = [card for card in _chore_cards(chores, today) if card["status"].is_due]
    recent_completions = Completion.objects.select_related("chore").order_by("-completed_on", "-created_at")[:20]
    context = {
        "today": today,
        "chore_cards": cards,
        "completion_form": CompletionForm(),
        "recent_completions": recent_completions,
    }
    return render(request, "chores/today.html", context)


@require_http_methods(["POST"])
def completion_create(request: HttpRequest, chore_id: int) -> HttpResponse:
    chore = get_object_or_404(Chore, pk=chore_id, is_archived=False)
    form = CompletionForm(request.POST)
    redirect_to = request.POST.get("next") or "chores:today"
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid completion date.")
    completed_on = form.cleaned_data["completed_on"]
    Completion.objects.get_or_create(chore=chore, completed_on=completed_on)
    return redirect(redirect_to)


@require_http_methods(["POST"])
def completion_undo(request: HttpRequest, completion_id: int) -> HttpResponse:
    completion = get_object_or_404(Completion, pk=completion_id)
    completion.delete()
    redirect_to = request.POST.get("next") or "chores:today"
    return redirect(redirect_to)
