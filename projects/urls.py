"""
URLs pour l'application projects
"""

from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="list"),
    path("featured/", views.featured_projects_view, name="featured"),
    path(
        "api/<slug:project_slug>/images/", views.project_images_api, name="images_api"
    ),
    path("<slug:slug>/", views.ProjectDetailView.as_view(), name="detail"),
]
