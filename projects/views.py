from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db import models
from .models import Project, ProjectCategory, Client


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
            .select_related("client", "metrics", "testimonial")
            .prefetch_related("categories", "images", "team_members__user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # Projets similaires basés sur les catégories et le client
        related_projects = (
            Project.objects.filter(
                models.Q(categories__in=project.categories.all())
                | models.Q(client=project.client),
                is_published=True,
            )
            .exclude(id=project.id)
            .select_related("client")
            .prefetch_related("categories")
            .distinct()[:6]
        )

        context["related_projects"] = related_projects

        # Informations supplémentaires pour le SEO et la structure
        context["page_title"] = f"{project.title} - Case Study"
        context["breadcrumbs"] = [
            {"name": "Accueil", "url": "/"},
            {"name": "Projets", "url": "/projects/"},
            {"name": project.title, "url": None},
        ]

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
                "urls": project.featured_image_urls,
            }
        )

    # Images additionnelles
    for img in project.images.all():
        images_data.append(
            {
                "type": "gallery",
                "title": img.title or f"Image {img.order}",
                "description": img.description,
                "urls": img.image_urls,
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

    # Ajouter les URLs multi-formats pour chaque projet
    projects_with_images = []
    for project in featured_projects:
        project_data = {"project": project, "image_urls": None}
        if project.featured_image:
            project_data["image_urls"] = project.featured_image_urls
        projects_with_images.append(project_data)

    return render(
        request,
        "projects/featured_projects.html",
        {"featured_projects": projects_with_images},
    )


def clients_api(request):
    """API pour récupérer les clients avec leurs logos en JSON"""
    clients = Client.objects.filter(is_active=True).order_by("order", "name")

    clients_data = []
    for client in clients:
        client_data = {
            "id": client.id,
            "name": client.name,
            "slug": client.slug,
            "website": client.website,
            "description": client.description,
            "logo_urls": client.logo_urls,
            "logo_white_urls": client.logo_white_urls,
            "projects_count": client.projects.filter(is_published=True).count(),
        }
        clients_data.append(client_data)

    return JsonResponse({"clients": clients_data})


def project_categories_api(request):
    """API pour récupérer les catégories de projets"""
    categories = ProjectCategory.objects.all().order_by("name")

    categories_data = []
    for category in categories:
        category_data = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "color": category.color,
            "projects_count": category.projects.filter(is_published=True).count(),
        }
        categories_data.append(category_data)

    return JsonResponse({"categories": categories_data})


class ProjectsByCategoryView(ListView):
    """Vue pour afficher les projets d'une catégorie spécifique"""

    model = Project
    template_name = "projects/projects_by_category.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(
            ProjectCategory, slug=self.kwargs["category_slug"]
        )
        return (
            Project.objects.filter(categories=self.category, is_published=True)
            .select_related("client")
            .prefetch_related("categories")
            .order_by("-order", "-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["all_categories"] = ProjectCategory.objects.all()
        return context


class ProjectsByClientView(ListView):
    """Vue pour afficher les projets d'un client spécifique"""

    model = Project
    template_name = "projects/projects_by_client.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        self.client = get_object_or_404(Client, slug=self.kwargs["client_slug"])
        return (
            Project.objects.filter(client=self.client, is_published=True)
            .select_related("client")
            .prefetch_related("categories")
            .order_by("-order", "-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client"] = self.client
        context["client_logo_urls"] = self.client.logo_urls
        return context


def search_projects(request):
    """Vue de recherche de projets"""
    query = request.GET.get("q", "")
    category_filter = request.GET.get("category", "")
    client_filter = request.GET.get("client", "")

    projects = Project.objects.filter(is_published=True)

    # Recherche textuelle
    if query:
        projects = projects.filter(
            models.Q(title__icontains=query)
            | models.Q(subtitle__icontains=query)
            | models.Q(description__icontains=query)
            | models.Q(content__icontains=query)
            | models.Q(client__name__icontains=query)
        )

    # Filtre par catégorie
    if category_filter:
        projects = projects.filter(categories__slug=category_filter)

    # Filtre par client
    if client_filter:
        projects = projects.filter(client__slug=client_filter)

    projects = (
        projects.select_related("client").prefetch_related("categories").distinct()
    )

    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "projects": page_obj,
        "query": query,
        "category_filter": category_filter,
        "client_filter": client_filter,
        "categories": ProjectCategory.objects.all(),
        "clients": Client.objects.filter(is_active=True),
        "total_results": projects.count(),
    }

    return render(request, "projects/search_results.html", context)


def project_stats_api(request):
    """API pour obtenir les statistiques des projets"""
    from django.db.models import Count, Q

    # Statistiques générales
    stats = {
        "total_projects": Project.objects.count(),
        "published_projects": Project.objects.filter(is_published=True).count(),
        "featured_projects": Project.objects.filter(
            is_featured=True, is_published=True
        ).count(),
        "draft_projects": Project.objects.filter(status="draft").count(),
        "completed_projects": Project.objects.filter(status="completed").count(),
        "active_clients": Client.objects.filter(is_active=True).count(),
        "total_categories": ProjectCategory.objects.count(),
    }

    # Projets par statut
    status_stats = Project.objects.values("status").annotate(count=Count("id"))
    stats["by_status"] = {item["status"]: item["count"] for item in status_stats}

    # Projets par catégorie
    category_stats = ProjectCategory.objects.annotate(
        project_count=Count("projects", filter=Q(projects__is_published=True))
    ).values("name", "color", "project_count")
    stats["by_category"] = list(category_stats)

    # Clients les plus actifs
    client_stats = (
        Client.objects.annotate(
            project_count=Count("projects", filter=Q(projects__is_published=True))
        )
        .filter(project_count__gt=0)
        .order_by("-project_count")[:5]
    )

    stats["top_clients"] = [
        {
            "name": client.name,
            "slug": client.slug,
            "project_count": client.project_count,
            "logo_url": client.logo_urls["thumbnail"] if client.logo else None,
        }
        for client in client_stats
    ]

    # Projets récents
    recent_projects = (
        Project.objects.filter(is_published=True)
        .select_related("client")
        .order_by("-created_at")[:5]
    )
    stats["recent_projects"] = [
        {
            "title": project.title,
            "slug": project.slug,
            "client": project.client.name,
            "status": project.status,
            "created_at": project.created_at.isoformat(),
            "thumbnail_url": (
                project.featured_image_urls["thumbnail"]
                if project.featured_image
                else None
            ),
        }
        for project in recent_projects
    ]

    return JsonResponse({"stats": stats})


def project_portfolio_api(request):
    """API pour le portfolio complet avec filtres optionnels"""
    # Paramètres de filtrage
    category_slug = request.GET.get("category")
    client_slug = request.GET.get("client")
    featured_only = request.GET.get("featured") == "true"
    limit = int(request.GET.get("limit", 20))

    # Construction de la requête
    projects = Project.objects.filter(is_published=True)

    if category_slug:
        projects = projects.filter(categories__slug=category_slug)

    if client_slug:
        projects = projects.filter(client__slug=client_slug)

    if featured_only:
        projects = projects.filter(is_featured=True)

    projects = projects.select_related("client").prefetch_related("categories")[:limit]

    # Formatage des données
    portfolio_data = []
    for project in projects:
        project_data = {
            "id": project.id,
            "title": project.title,
            "slug": project.slug,
            "subtitle": project.subtitle,
            "description": project.description,
            "client": {
                "name": project.client.name,
                "slug": project.client.slug,
                "logo_urls": project.client.logo_urls,
            },
            "categories": [
                {"name": cat.name, "slug": cat.slug, "color": cat.color}
                for cat in project.categories.all()
            ],
            "image_urls": project.featured_image_urls,
            "is_featured": project.is_featured,
            "status": project.status,
            "duration_days": project.duration_in_days,
            "created_at": project.created_at.isoformat(),
        }

        # Ajouter les métriques si disponibles
        if hasattr(project, "metrics"):
            project_data["metrics"] = {
                "page_views_increase": project.metrics.page_views_increase,
                "conversion_rate_increase": project.metrics.conversion_rate_increase,
                "seo_score": project.metrics.seo_score,
                "performance_score": project.metrics.performance_score,
            }

        # Ajouter le témoignage si disponible
        if hasattr(project, "testimonial"):
            project_data["testimonial"] = {
                "client_name": project.testimonial.client_name,
                "client_position": project.testimonial.client_position,
                "quote": project.testimonial.quote,
                "rating": project.testimonial.rating,
                "client_photo_urls": project.testimonial.client_photo_urls,
            }

        portfolio_data.append(project_data)

    return JsonResponse(
        {
            "projects": portfolio_data,
            "total_count": projects.count(),
            "filters_applied": {
                "category": category_slug,
                "client": client_slug,
                "featured_only": featured_only,
                "limit": limit,
            },
        }
    )
