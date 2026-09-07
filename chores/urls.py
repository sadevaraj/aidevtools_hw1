from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.chore_list, name="list"),
    path("today/", views.today_dashboard, name="today"),
    path("chore/<int:chore_id>/edit/", views.chore_edit, name="edit"),
    path("chore/<int:chore_id>/archive/", views.chore_archive, name="archive"),
    path("chore/<int:chore_id>/complete/", views.completion_create, name="complete"),
    path("completion/<int:completion_id>/undo/", views.completion_undo, name="undo"),
]
