from django.shortcuts import render
from projects.models import Project


# Create your views here.
def index(request):
    # Récupérer les projets mis en avant pour la page d'accueil
    featured_projects = Project.objects.filter(
        is_featured=True, is_published=True
    ).order_by("-created_at")[:3]

    context = {
        "featured_projects": featured_projects,
    }
    return render(request, "index.html", context)
