"""
Configuration avancée pour l'administration des projets
"""

from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class ProjectsAdminSite(AdminSite):
    """Site d'administration personnalisé pour les projets"""
    
    site_header = _("WebTech Solutions - Administration")
    site_title = _("WebTech Admin")
    index_title = _("Tableau de bord des projets")
    
    def index(self, request, extra_context=None):
        """Personnalise la page d'accueil de l'admin"""
        extra_context = extra_context or {}
        
        # Ajouter des statistiques rapides
        from .models import Project, Client, ProjectCategory, ProjectImage
        
        stats = {
            'total_projects': Project.objects.count(),
            'published_projects': Project.objects.filter(is_published=True).count(),
            'featured_projects': Project.objects.filter(is_featured=True).count(),
            'total_clients': Client.objects.filter(is_active=True).count(),
            'total_categories': ProjectCategory.objects.count(),
            'total_images': ProjectImage.objects.count(),
        }
        
        # Projets récents
        recent_projects = Project.objects.select_related('client').order_by('-created_at')[:5]
        
        # Projets par statut
        project_status_stats = {}
        for status in Project.objects.values_list('status', flat=True).distinct():
            project_status_stats[status] = Project.objects.filter(status=status).count()
        
        extra_context.update({
            'stats': stats,
            'recent_projects': recent_projects,
            'project_status_stats': project_status_stats,
        })
        
        return super().index(request, extra_context)


# Couleurs pour les différents statuts
STATUS_COLORS = {
    'draft': '#6c757d',
    'in_progress': '#ffc107', 
    'completed': '#28a745',
    'on_hold': '#fd7e14',
    'cancelled': '#dc3545',
}

# Configuration des transformations d'images
IMAGE_TRANSFORMATIONS = {
    'thumbnail': {
        'width': 300,
        'height': 200,
        'crop': 'fill',
        'quality': 'auto',
        'fetch_format': 'auto',
    },
    'medium': {
        'width': 600,
        'height': 400,
        'crop': 'limit',
        'quality': 'auto',
        'fetch_format': 'auto',
    },
    'large': {
        'width': 1200,
        'height': 800,
        'crop': 'limit',
        'quality': 'auto',
        'fetch_format': 'auto',
    },
}

# Configuration des permissions
ADMIN_PERMISSIONS = {
    'can_view_stats': ['projects.view_project'],
    'can_manage_featured': ['projects.change_project'],
    'can_manage_clients': ['projects.add_client', 'projects.change_client'],
}

# Messages d'aide pour l'admin
HELP_TEXTS = {
    'project_status': {
        'draft': 'Projet en cours de création, non visible publiquement',
        'in_progress': 'Projet en cours de développement',
        'completed': 'Projet terminé et livré au client',
        'on_hold': 'Projet temporairement suspendu',
        'cancelled': 'Projet annulé',
    },
    'image_formats': {
        'original': 'Image source en qualité originale',
        'large': 'Version optimisée pour l\'affichage en grand format',
        'thumbnail': 'Miniature pour les listes et aperçus',
    },
}

# Configuration des exports
EXPORT_FORMATS = ['csv', 'xlsx', 'pdf']

# Champs de recherche avancée
ADVANCED_SEARCH_FIELDS = {
    'Project': ['title', 'subtitle', 'description', 'content', 'client__name'],
    'Client': ['name', 'description', 'website'],
    'ProjectCategory': ['name', 'description'],
}

# Configuration des filtres
ADMIN_FILTERS = {
    'Project': {
        'date_filters': ['created_at', 'published_at', 'start_date', 'end_date'],
        'choice_filters': ['status', 'is_featured', 'is_published'],
        'relation_filters': ['client', 'categories'],
    },
    'Client': {
        'boolean_filters': ['is_active'],
        'date_filters': ['created_at'],
    },
}

# Configuration des actions en lot
BULK_ACTIONS = {
    'Project': [
        'mark_as_published',
        'mark_as_unpublished', 
        'mark_as_featured',
        'unmark_as_featured',
        'export_selected',
    ],
    'Client': [
        'mark_as_active',
        'mark_as_inactive',
        'export_selected',
    ],
}

# Configuration de la pagination
ADMIN_PAGINATION = {
    'default_per_page': 25,
    'max_per_page': 100,
}

# Configuration des notifications
ADMIN_NOTIFICATIONS = {
    'success_messages': {
        'project_published': 'Le projet "{}" a été publié avec succès.',
        'client_created': 'Le client "{}" a été créé avec succès.',
        'bulk_update': '{} éléments ont été mis à jour.',
    },
    'warning_messages': {
        'missing_image': 'Attention: Ce projet n\'a pas d\'image principale.',
        'incomplete_project': 'Ce projet semble incomplet.',
    },
}
