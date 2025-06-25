from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from .models import Project, ProjectCategory, Client
from core.cloudinary_utils import generate_responsive_urls


class ProjectListView(ListView):
    """Vue pour lister tous les projets publiés"""

    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Project.objects.filter(is_published=True)
            .select_related("client")
            .prefetch_related("categories")
        )

        # Filtrage par catégorie
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)

        # Tri
        order_by = self.request.GET.get("order_by", "-created_at")
        if order_by in ["-created_at", "-order", "title"]:
            queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ProjectCategory.objects.all()
        context["current_category"] = self.request.GET.get("category")
        return context


class ProjectDetailView(DetailView):
    """Vue détaillée d'un projet"""

    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Project.objects.filter(is_published=True)
            .select_related("client")
            .prefetch_related("categories", "images", "team_members__user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # Générer les URLs responsives pour l'image principale
        if project.featured_image:
            context["featured_image_urls"] = generate_responsive_urls(
                str(project.featured_image)
            )

        # Images additionnelles avec URLs responsives
        additional_images = []
        for img in project.images.all():
            additional_images.append(
                {"image": img, "urls": generate_responsive_urls(str(img.image))}
            )
        context["additional_images"] = additional_images

        # Projets similaires
        context["related_projects"] = (
            Project.objects.filter(
                categories__in=project.categories.all(), is_published=True
            )
            .exclude(id=project.id)
            .distinct()[:3]
        )

        return context


def project_images_api(request, project_slug):
    """API pour récupérer les images d'un projet en JSON"""
    project = get_object_or_404(Project, slug=project_slug, is_published=True)

    images_data = []

    # Image principale
    if project.featured_image:
        images_data.append(
            {
                "type": "featured",
                "title": project.title,
                "urls": generate_responsive_urls(str(project.featured_image)),
            }
        )

    # Images additionnelles
    for img in project.images.all():
        images_data.append(
            {
                "type": "gallery",
                "title": img.title or f"Image {img.order}",
                "description": img.description,
                "urls": generate_responsive_urls(str(img.image)),
            }
        )

    return JsonResponse({"project": project.title, "images": images_data})


def featured_projects_view(request):
    """Vue pour les projets mis en avant"""
    featured_projects = (
        Project.objects.filter(is_published=True, is_featured=True)
        .select_related("client")
        .prefetch_related("categories")[:6]
    )

    # Ajouter les URLs responsives pour chaque projet
    projects_with_images = []
    for project in featured_projects:
        project_data = {"project": project, "image_urls": None}
        if project.featured_image:
            project_data["image_urls"] = generate_responsive_urls(
                str(project.featured_image)
            )
        projects_with_images.append(project_data)

    return render(
        request,
        "projects/featured_projects.html",
        {"featured_projects": projects_with_images},
    )
