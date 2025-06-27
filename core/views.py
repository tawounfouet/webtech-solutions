from django.shortcuts import render
from projects.models import Project, Client


# Create your views here.
def index(request):
    # Récupérer les projets mis en avant pour la page d'accueil
    featured_projects = Project.objects.filter(
        is_featured=True, is_published=True
    ).order_by("-created_at")[:3]

    # Récupérer les clients actifs pour le slider de logos
    active_clients = Client.objects.filter(is_active=True).order_by("order", "name")

    context = {
        "featured_projects": featured_projects,
        "active_clients": active_clients,
    }
    return render(request, "index.html", context)
