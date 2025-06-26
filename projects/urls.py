"""
URLs pour l'application projects
"""

from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="list"),
    path("search/", views.search_projects, name="search"),
    path("featured/", views.featured_projects_view, name="featured"),
    path("category/<slug:category_slug>/", views.ProjectsByCategoryView.as_view(), name="by_category"),
    path("client/<slug:client_slug>/", views.ProjectsByClientView.as_view(), name="by_client"),
    
    # APIs
    path("api/clients/", views.clients_api, name="clients_api"),
    path("api/categories/", views.project_categories_api, name="categories_api"),
    path("api/stats/", views.project_stats_api, name="stats_api"),
    path("api/portfolio/", views.project_portfolio_api, name="portfolio_api"),
    path("api/<slug:project_slug>/images/", views.project_images_api, name="images_api"),
    
    # Détail du projet (doit être en dernier pour éviter les conflits)
    path("<slug:slug>/", views.ProjectDetailView.as_view(), name="detail"),
]
