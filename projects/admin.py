from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from cloudinary import CloudinaryImage
from core.cloudinary_forms import CloudinaryImageField
from .models import (
    ProjectCategory,
    Client,
    Project,
    ProjectImage,
    ProjectTeamMember,
    ProjectTestimonial,
    ProjectMetrics,
)

# Constantes pour les messages d'affichage
ERROR_DISPLAY_MESSAGE = "Erreur d'affichage"
NO_IMAGE_MESSAGE = "Aucune image"
NO_LOGO_MESSAGE = "Aucun logo"


# Forms personnalisés pour l'administration
class ClientAdminForm(forms.ModelForm):
    """Form personnalisé pour le modèle Client avec widgets Cloudinary optimisés"""

    logo = CloudinaryImageField(
        required=False,
        options={
            "folder": "clients/logos",
            "width": 300,
            "height": 300,
            "crop": "fit",
            "fetch_format": "auto",
            "quality": "auto",
        },
        help_text="Logo principal du client (300x300px recommandé)",
    )

    logo_white = CloudinaryImageField(
        required=False,
        options={
            "folder": "clients/logos/white",
            "width": 300,
            "height": 300,
            "crop": "fit",
            "fetch_format": "auto",
            "quality": "auto",
        },
        help_text="Version blanche du logo pour fonds sombres",
    )

    class Meta:
        model = Client
        fields = [
            "name",
            "slug",
            "logo",
            "logo_white",
            "website",
            "description",
            "is_active",
        ]


class ProjectAdminForm(forms.ModelForm):
    """Form personnalisé pour le modèle Project avec widgets Cloudinary optimisés"""

    featured_image = CloudinaryImageField(
        options={
            "folder": "projects/featured",
            "width": 1200,
            "height": 800,
            "crop": "fill",
            "fetch_format": "auto",
            "quality": "auto",
        },
        help_text="Image principale du projet (1200x800px recommandé)",
    )

    thumbnail = CloudinaryImageField(
        required=False,
        options={
            "folder": "projects/thumbnails",
            "width": 400,
            "height": 300,
            "crop": "fill",
            "fetch_format": "auto",
            "quality": "auto",
        },
        help_text="Miniature du projet (générée automatiquement si vide)",
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "slug",
            "subtitle",
            "description",
            "content",
            "client",
            "categories",
            "featured_image",
            "thumbnail",
            "status",
            "start_date",
            "end_date",
            "budget",
            "is_featured",
            "is_published",
            "order",
        ]


class ProjectImageAdminForm(forms.ModelForm):
    """Form personnalisé pour le modèle ProjectImage"""

    image = CloudinaryImageField(
        options={
            "folder": "projects/gallery",
            "width": 1200,
            "height": 800,
            "crop": "limit",
            "fetch_format": "auto",
            "quality": "auto",
        },
        help_text="Image de galerie du projet (1200x800px recommandé)",
    )

    class Meta:
        model = ProjectImage
        fields = ["project", "image", "title", "description", "order"]


class ProjectTestimonialAdminForm(forms.ModelForm):
    """Form personnalisé pour le modèle ProjectTestimonial"""

    client_photo = CloudinaryImageField(
        required=False,
        options={
            "folder": "testimonials",
            "width": 150,
            "height": 150,
            "crop": "fill",
            "gravity": "face",
            "fetch_format": "auto",
            "quality": "auto",
        },
        help_text="Photo du client (150x150px, détection automatique du visage)",
    )

    class Meta:
        model = ProjectTestimonial
        fields = [
            "project",
            "client_name",
            "client_position",
            "client_photo",
            "quote",
            "rating",
            "is_featured",
        ]


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color_preview", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; display: inline-block;"></div>',
            obj.color,
        )

    color_preview.short_description = "Couleur"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm
    list_display = [
        "name",
        "slug",
        "logo_preview",
        "website",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}

    def logo_preview(self, obj):
        """Affiche un aperçu du logo Cloudinary"""
        if obj.logo:
            try:
                thumbnail_url = CloudinaryImage(str(obj.logo)).build_url(
                    width=50, height=50, crop="fill", format="auto", quality="auto"
                )
                return format_html(
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;">',
                    thumbnail_url,
                )
            except Exception:
                return ERROR_DISPLAY_MESSAGE
        return NO_LOGO_MESSAGE

    logo_preview.short_description = "Logo"


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    form = ProjectImageAdminForm
    extra = 1
    fields = ["image_preview", "image", "title", "order"]
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        """Affiche un aperçu de l'image Cloudinary"""
        if obj.image:
            try:
                thumbnail_url = CloudinaryImage(str(obj.image)).build_url(
                    width=100, height=100, crop="fill", format="auto", quality="auto"
                )
                return format_html(
                    '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 4px;">',
                    thumbnail_url,
                )
            except Exception:
                return ERROR_DISPLAY_MESSAGE
        return NO_IMAGE_MESSAGE

    image_preview.short_description = "Aperçu"


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 1
    fields = ["user", "role", "is_lead"]


class ProjectTestimonialInline(admin.StackedInline):
    model = ProjectTestimonial
    form = ProjectTestimonialAdminForm
    extra = 0
    fields = ["client_name", "client_position", "client_photo", "quote", "rating", "is_featured"]


class ProjectMetricsInline(admin.StackedInline):
    model = ProjectMetrics
    extra = 0
    fieldsets = (
        (
            "Métriques de Performance",
            {
                "fields": (
                    "page_views_increase",
                    "conversion_rate_increase",
                    "bounce_rate_decrease",
                    "loading_time_improvement",
                )
            },
        ),
        ("Métriques Business", {"fields": ("revenue_increase", "leads_increase")}),
        (
            "Métriques Techniques",
            {"fields": ("seo_score", "accessibility_score", "performance_score")},
        ),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = [
        "title",
        "client",
        "featured_image_preview",
        "status",
        "is_published",
        "is_featured",
        "start_date",
        "created_at",
    ]
    list_filter = [
        "status",
        "is_published",
        "is_featured",
        "categories",
        "client",
        "created_at",
    ]
    search_fields = ["title", "subtitle", "description", "client__name"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["categories"]

    fieldsets = (
        (
            "Informations principales",
            {
                "fields": (
                    "title",
                    "slug",
                    "subtitle",
                    "description",
                    "content",
                    "client",
                )
            },
        ),
        (
            "Images",
            {"fields": ("featured_image_preview", "featured_image", "thumbnail")},
        ),
        ("Catégories et Équipe", {"fields": ("categories",)}),
        ("Métadonnées", {"fields": ("status", "start_date", "end_date", "budget")}),
        (
            "Paramètres d'affichage",
            {"fields": ("is_published", "is_featured", "order", "published_at")},
        ),
    )

    readonly_fields = ["featured_image_preview"]

    inlines = [
        ProjectImageInline,
        ProjectTeamMemberInline,
        ProjectTestimonialInline,
        ProjectMetricsInline,
    ]

    def featured_image_preview(self, obj):
        """Affiche un aperçu de l'image principale"""
        if obj.featured_image:
            try:
                thumbnail_url = CloudinaryImage(str(obj.featured_image)).build_url(
                    width=200, height=150, crop="fill", format="auto", quality="auto"
                )
                return format_html(
                    '<img src="{}" style="width: 200px; height: 150px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">',
                    thumbnail_url,
                )
            except Exception:
                return ERROR_DISPLAY_MESSAGE
        return NO_IMAGE_MESSAGE

    featured_image_preview.short_description = "Aperçu de l'image principale"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("client")
            .prefetch_related("categories")
        )


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    form = ProjectImageAdminForm
    list_display = ["project", "title", "order", "created_at"]
    list_filter = ["project", "created_at"]
    search_fields = ["project__title", "title"]


@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "user", "role", "is_lead", "joined_at"]
    list_filter = ["is_lead", "role", "joined_at"]
    search_fields = [
        "project__title",
        "user__username",
        "user__first_name",
        "user__last_name",
        "role",
    ]


@admin.register(ProjectTestimonial)
class ProjectTestimonialAdmin(admin.ModelAdmin):
    form = ProjectTestimonialAdminForm
    list_display = ["project", "client_name", "rating", "is_featured", "created_at"]
    list_filter = ["rating", "is_featured", "created_at"]
    search_fields = ["project__title", "client_name", "quote"]


@admin.register(ProjectMetrics)
class ProjectMetricsAdmin(admin.ModelAdmin):
    list_display = [
        "project",
        "page_views_increase",
        "conversion_rate_increase",
        "seo_score",
        "updated_at",
    ]
    list_filter = ["updated_at"]
    search_fields = ["project__title"]
