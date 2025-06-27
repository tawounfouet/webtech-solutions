from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db import models
from django.forms import TextInput, Textarea
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import (
    ProjectCategory,
    Client,
    Project,
    ProjectImage,
    ProjectTeamMember,
    ProjectTestimonial,
    ProjectMetrics,
)


class ColoredTextWidget(TextInput):
    """Widget personnalisé pour afficher la couleur"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({"type": "color"})


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "color_preview", "description_short", "created_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "20"})},
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "color" in form.base_fields:
            form.base_fields["color"].widget = ColoredTextWidget()

        # Configurer CKEditor5 pour le champ description
        if "description" in form.base_fields:
            form.base_fields["description"].widget = CKEditor5Widget(
                config_name="default"
            )

        return form

    def color_preview(self, obj):
        """Affiche un aperçu de la couleur"""
        if obj.color:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ddd; border-radius: 3px; display: inline-block;"></div> <span style="margin-left: 8px;">{}</span>',
                obj.color,
                obj.color,
            )
        return "-"

    color_preview.short_description = "Couleur"

    def description_short(self, obj):
        """Affiche une version tronquée de la description"""
        if obj.description:
            return (
                obj.description[:50] + "..."
                if len(obj.description) > 50
                else obj.description
            )
        return "-"

    description_short.short_description = "Description"


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ["image_preview", "image", "title", "order"]
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        """Affiche une prévisualisation de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        elif obj.image_thumbnail:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.image_thumbnail.url,
            )
        return mark_safe('<span style="color: #999;">Pas d\'image</span>')

    image_preview.short_description = "Aperçu"


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 1
    fields = ["user", "role", "is_lead"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


class ProjectTestimonialInline(admin.StackedInline):
    model = ProjectTestimonial
    fields = [
        "client_photo_preview",
        ("client_photo", "client_photo_large", "client_photo_thumbnail"),
        ("client_name", "client_position"),
        "quote",
        ("rating", "is_featured"),
    ]
    readonly_fields = ["client_photo_preview"]

    def client_photo_preview(self, obj):
        """Affiche une prévisualisation de la photo client"""
        if obj and obj.client_photo:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 50%; border: 2px solid #ddd;" />',
                obj.client_photo.url,
            )
        elif obj and obj.client_photo_thumbnail:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 50%; border: 2px solid #ddd;" />',
                obj.client_photo_thumbnail.url,
            )
        return mark_safe('<span style="color: #999;">Pas de photo</span>')

    client_photo_preview.short_description = "Photo actuelle"


class ProjectMetricsInline(admin.StackedInline):
    model = ProjectMetrics
    fields = [
        ("page_views_increase", "conversion_rate_increase"),
        ("bounce_rate_decrease", "loading_time_improvement"),
        ("revenue_increase", "leads_increase"),
        ("seo_score", "accessibility_score", "performance_score"),
    ]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "logo_preview",
        "logo_white_preview",
        "website_link",
        "is_active",
        "order",
        "projects_count",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        "created_at",
        "updated_at",
        "logo_preview_large",
        "logo_white_preview_large",
    ]

    fieldsets = (
        (
            "Informations générales",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "website",
                    "is_active",
                    "order",
                )
            },
        ),
        (
            "Logo principal",
            {
                "fields": (
                    "logo_preview_large",
                    ("logo", "logo_large", "logo_thumbnail"),
                )
            },
        ),
        (
            "Logo blanc",
            {
                "fields": (
                    "logo_white_preview_large",
                    ("logo_white", "logo_white_large", "logo_white_thumbnail"),
                )
            },
        ),
        (
            "Métadonnées",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def logo_preview(self, obj):
        """Affiche une prévisualisation du logo"""
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 30px; object-fit: contain;" />',
                obj.logo.url,
            )
        return "-"

    logo_preview.short_description = "Logo"

    def logo_white_preview(self, obj):
        """Affiche une prévisualisation du logo blanc"""
        if obj.logo_white:
            return format_html(
                '<img src="{}" style="width: 50px; height: 30px; object-fit: contain; background: #333; padding: 2px;" />',
                obj.logo_white.url,
            )
        return "-"

    logo_white_preview.short_description = "Logo blanc"

    def logo_preview_large(self, obj):
        """Affiche une grande prévisualisation du logo"""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 100px; object-fit: contain; border: 1px solid #ddd; padding: 10px;" />',
                obj.logo.url,
            )
        return mark_safe('<span style="color: #999;">Aucun logo</span>')

    logo_preview_large.short_description = "Aperçu du logo"

    def logo_white_preview_large(self, obj):
        """Affiche une grande prévisualisation du logo blanc"""
        if obj.logo_white:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 100px; object-fit: contain; background: #333; padding: 10px; border: 1px solid #ddd;" />',
                obj.logo_white.url,
            )
        return mark_safe('<span style="color: #999;">Aucun logo blanc</span>')

    logo_white_preview_large.short_description = "Aperçu du logo blanc"

    def website_link(self, obj):
        """Affiche le lien du site web comme lien cliquable"""
        if obj.website:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0073aa;">{}</a>',
                obj.website,
                obj.website[:30] + "..." if len(obj.website) > 30 else obj.website,
            )
        return "-"

    website_link.short_description = "Site web"

    def projects_count(self, obj):
        """Affiche le nombre de projets du client"""
        count = obj.projects.count()
        if count > 0:
            url = (
                reverse("admin:projects_project_changelist")
                + f"?client__id__exact={obj.id}"
            )
            return format_html(
                '<a href="{}" style="color: #0073aa;">{} projet{}</a>',
                url,
                count,
                "s" if count > 1 else "",
            )
        return "0 projet"

    projects_count.short_description = "Projets"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Configurer CKEditor5 pour le champ description
        if "description" in form.base_fields:
            form.base_fields["description"].widget = CKEditor5Widget(
                config_name="default"
            )

        return form

    # Actions personnalisées
    def mark_clients_as_active(modeladmin, request, queryset):
        """Marque les clients sélectionnés comme actifs"""
        updated = queryset.update(is_active=True)
        modeladmin.message_user(
            request, f"{updated} client(s) marqué(s) comme actif(s).", level="success"
        )

    mark_clients_as_active.short_description = "Marquer comme actif"

    def mark_clients_as_inactive(modeladmin, request, queryset):
        """Marque les clients sélectionnés comme inactifs"""
        updated = queryset.update(is_active=False)
        modeladmin.message_user(
            request, f"{updated} client(s) marqué(s) comme inactif(s).", level="success"
        )

    mark_clients_as_inactive.short_description = "Marquer comme inactif"

    actions = [mark_clients_as_active, mark_clients_as_inactive]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "featured_image_preview",
        "client",
        "status_colored",
        "categories_display",
        "is_featured",
        "is_published",
        "created_at",
    ]
    list_filter = [
        "status",
        "is_featured",
        "is_published",
        "categories",
        "client",
        "created_at",
    ]
    search_fields = ["title", "subtitle", "description", "client__name"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = [
        "created_at",
        "updated_at",
        "duration_display",
        "featured_image_preview_large",
        "thumbnail_preview_large",
    ]
    filter_horizontal = ["categories"]
    date_hierarchy = "created_at"

    # Configuration des widgets CKEditor5
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "20"})},
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Configurer CKEditor5 pour le champ content avec la configuration étendue
        if "content" in form.base_fields:
            form.base_fields["content"].widget = CKEditor5Widget(config_name="extends")

        return form

    fieldsets = (
        (
            "Informations générales",
            {
                "fields": (
                    ("title", "slug"),
                    "subtitle",
                    "description",
                    "content",
                    ("client", "status"),
                    "categories",
                )
            },
        ),
        (
            "Images",
            {
                "fields": (
                    "featured_image_preview_large",
                    ("featured_image", "featured_image_large"),
                    "thumbnail_preview_large",
                    "thumbnail",
                )
            },
        ),
        (
            "Projet",
            {
                "fields": (
                    ("start_date", "end_date", "duration_display"),
                    "budget",
                )
            },
        ),
        (
            "Publication",
            {
                "fields": (
                    ("is_featured", "is_published"),
                    ("order", "published_at"),
                )
            },
        ),
        (
            "Métadonnées",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [
        ProjectImageInline,
        ProjectTeamMemberInline,
        ProjectTestimonialInline,
        ProjectMetricsInline,
    ]

    def featured_image_preview(self, obj):
        """Affiche une prévisualisation de l'image principale"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.featured_image.url,
            )
        elif obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail.url,
            )
        return mark_safe('<span style="color: #999;">Pas d\'image</span>')

    featured_image_preview.short_description = "Image"

    def featured_image_preview_large(self, obj):
        """Affiche une grande prévisualisation de l'image principale"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd;" />',
                obj.featured_image.url,
            )
        return mark_safe('<span style="color: #999;">Aucune image principale</span>')

    featured_image_preview_large.short_description = "Aperçu de l'image principale"

    def thumbnail_preview_large(self, obj):
        """Affiche une grande prévisualisation de la miniature"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 150px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd;" />',
                obj.thumbnail.url,
            )
        return mark_safe('<span style="color: #999;">Aucune miniature</span>')

    thumbnail_preview_large.short_description = "Aperçu de la miniature"

    def status_colored(self, obj):
        """Affiche le statut avec une couleur"""
        colors = {
            "draft": "#6c757d",
            "in_progress": "#ffc107",
            "completed": "#28a745",
            "on_hold": "#fd7e14",
            "cancelled": "#dc3545",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = "Statut"

    def categories_display(self, obj):
        """Affiche les catégories avec leurs couleurs"""
        categories = obj.categories.all()
        if not categories:
            return "-"

        badges = []
        for category in categories[:3]:  # Limite à 3 catégories
            badges.append(
                format_html(
                    '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; margin-right: 2px;">{}</span>',
                    category.color,
                    category.name,
                )
            )

        result = "".join(badges)
        if categories.count() > 3:
            result += format_html(
                '<span style="color: #666;">+{}</span>', categories.count() - 3
            )

        return mark_safe(result)

    categories_display.short_description = "Catégories"

    def duration_display(self, obj):
        """Affiche la durée du projet"""
        duration = obj.duration_in_days
        if duration is not None:
            if duration == 0:
                return "Même jour"
            elif duration == 1:
                return "1 jour"
            elif duration < 30:
                return f"{duration} jours"
            elif duration < 365:
                months = duration // 30
                return f"{months} mois"
            else:
                years = duration // 365
                return f"{years} an{'s' if years > 1 else ''}"
        return "-"

    duration_display.short_description = "Durée"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("client")
            .prefetch_related("categories")
        )

    # Actions personnalisées
    def mark_as_published(modeladmin, request, queryset):
        """Marque les projets sélectionnés comme publiés"""
        updated = queryset.update(is_published=True)
        modeladmin.message_user(
            request, f"{updated} projet(s) marqué(s) comme publié(s).", level="success"
        )

    mark_as_published.short_description = "Marquer comme publié"

    def mark_as_unpublished(modeladmin, request, queryset):
        """Marque les projets sélectionnés comme non publiés"""
        updated = queryset.update(is_published=False)
        modeladmin.message_user(
            request,
            f"{updated} projet(s) marqué(s) comme non publié(s).",
            level="success",
        )

    mark_as_unpublished.short_description = "Marquer comme non publié"

    def mark_as_featured(modeladmin, request, queryset):
        """Marque les projets sélectionnés comme mis en avant"""
        updated = queryset.update(is_featured=True)
        modeladmin.message_user(
            request,
            f"{updated} projet(s) marqué(s) comme mis en avant.",
            level="success",
        )

    mark_as_featured.short_description = "Mettre en avant"

    def unmark_as_featured(modeladmin, request, queryset):
        """Enlève la mise en avant des projets sélectionnés"""
        updated = queryset.update(is_featured=False)
        modeladmin.message_user(
            request,
            f"{updated} projet(s) retiré(s) de la mise en avant.",
            level="success",
        )

    unmark_as_featured.short_description = "Retirer de la mise en avant"

    actions = [
        mark_as_published,
        mark_as_unpublished,
        mark_as_featured,
        unmark_as_featured,
    ]


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ["project", "image_preview", "title", "order", "created_at"]
    list_filter = ["project", "created_at"]
    search_fields = ["title", "description", "project__title"]
    readonly_fields = ["created_at", "image_preview_large"]

    fieldsets = (
        ("Informations", {"fields": ("project", "title", "description", "order")}),
        (
            "Image",
            {
                "fields": (
                    "image_preview_large",
                    ("image", "image_large", "image_thumbnail"),
                )
            },
        ),
        ("Métadonnées", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def image_preview(self, obj):
        """Affiche une prévisualisation de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Image"

    def image_preview_large(self, obj):
        """Affiche une grande prévisualisation de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd;" />',
                obj.image.url,
            )
        return mark_safe('<span style="color: #999;">Aucune image</span>')

    image_preview_large.short_description = "Aperçu de l'image"


@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "role", "is_lead", "joined_at"]
    list_filter = ["is_lead", "role", "joined_at"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "project__title",
        "role",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "project")


@admin.register(ProjectTestimonial)
class ProjectTestimonialAdmin(admin.ModelAdmin):
    list_display = [
        "client_name",
        "project",
        "rating_stars",
        "is_featured",
        "created_at",
    ]
    list_filter = ["rating", "is_featured", "created_at"]
    search_fields = ["client_name", "client_position", "quote", "project__title"]
    readonly_fields = ["created_at", "client_photo_preview_large"]

    fieldsets = (
        (
            "Client",
            {
                "fields": (
                    ("client_name", "client_position"),
                    "client_photo_preview_large",
                    ("client_photo", "client_photo_large", "client_photo_thumbnail"),
                )
            },
        ),
        (
            "Témoignage",
            {
                "fields": (
                    "project",
                    "quote",
                    ("rating", "is_featured"),
                )
            },
        ),
        ("Métadonnées", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def rating_stars(self, obj):
        """Affiche la note sous forme d'étoiles"""
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html(
            '<span style="color: #ffc107; font-size: 16px;">{}</span> <span style="color: #666;">({}/5)</span>',
            stars,
            obj.rating,
        )

    rating_stars.short_description = "Note"

    def client_photo_preview_large(self, obj):
        """Affiche une grande prévisualisation de la photo client"""
        if obj.client_photo:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 50%; border: 2px solid #ddd;" />',
                obj.client_photo.url,
            )
        return mark_safe('<span style="color: #999;">Aucune photo</span>')

    client_photo_preview_large.short_description = "Photo du client"


@admin.register(ProjectMetrics)
class ProjectMetricsAdmin(admin.ModelAdmin):
    list_display = ["project", "performance_summary", "seo_score", "created_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["project__title"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Métriques de performance",
            {
                "fields": (
                    ("page_views_increase", "conversion_rate_increase"),
                    ("bounce_rate_decrease", "loading_time_improvement"),
                )
            },
        ),
        ("Métriques business", {"fields": (("revenue_increase", "leads_increase"),)}),
        (
            "Scores techniques",
            {"fields": (("seo_score", "accessibility_score", "performance_score"),)},
        ),
        (
            "Métadonnées",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def performance_summary(self, obj):
        """Affiche un résumé des performances"""
        metrics = []

        if obj.page_views_increase:
            color = "#28a745" if obj.page_views_increase > 0 else "#dc3545"
            metrics.append(
                format_html(
                    '<span style="color: {};">Trafic: +{}%</span>',
                    color,
                    obj.page_views_increase,
                )
            )

        if obj.conversion_rate_increase:
            color = "#28a745" if obj.conversion_rate_increase > 0 else "#dc3545"
            metrics.append(
                format_html(
                    '<span style="color: {};">Conversion: +{}%</span>',
                    color,
                    obj.conversion_rate_increase,
                )
            )

        return mark_safe(" | ".join(metrics)) if metrics else "-"

    performance_summary.short_description = "Résumé performances"


# Configuration de l'admin
admin.site.site_header = "Administration WebTech Solutions"
admin.site.site_title = "WebTech Admin"
admin.site.index_title = "Gestion des projets"
