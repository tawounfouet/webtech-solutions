from django.db import models
from django.utils.text import slugify
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from cloudinary.models import CloudinaryField
from django_ckeditor_5.fields import CKEditor5Field
import cloudinary
import logging

# from django.contrib.auth.models import User
# Importing User model from Django settings to ensure compatibility with custom user models
# from django settings import AUTH_USER_MODEL
from django.conf import settings

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL


class ProjectCategory(models.Model):
    """Catégorie de projet (ex: Branding, UI/UX, Development, etc.)"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = CKEditor5Field("Description", config_name="default", blank=True)
    color = models.CharField(
        max_length=7, default="#6c757d", help_text="Code couleur hexadécimal"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie de projet"
        verbose_name_plural = "Catégories de projet"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Client(models.Model):
    """Client pour lequel le projet a été réalisé"""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    # Cloudinary public_id pour référence et suppression
    logo_cloudinary_public_id = models.CharField(max_length=255, blank=True, default="")
    logo_white_cloudinary_public_id = models.CharField(
        max_length=255, blank=True, default=""
    )

    # Version originale du logo
    logo = CloudinaryField(
        "client_logo",
        resource_type="image",
        folder="clients/logos/original",
        null=True,
        blank=True,
    )

    # Version pour affichage principal
    logo_large = CloudinaryField(
        "client_logo_large",
        resource_type="image",
        folder="clients/logos/large",
        null=True,
        blank=True,
        transformation=[
            {"width": 400, "crop": "limit"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # Version miniature du logo
    logo_thumbnail = CloudinaryField(
        "client_logo_thumbnail",
        resource_type="image",
        folder="clients/logos/thumbnails",
        null=True,
        blank=True,
        transformation=[
            {"width": 150, "height": 150, "crop": "fit"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # Version originale du logo blanc
    logo_white = CloudinaryField(
        "client_logo_white",
        resource_type="image",
        folder="clients/logos/white/original",
        null=True,
        blank=True,
    )

    # Version pour affichage principal du logo blanc
    logo_white_large = CloudinaryField(
        "client_logo_white_large",
        resource_type="image",
        folder="clients/logos/white/large",
        null=True,
        blank=True,
        transformation=[
            {"width": 400, "crop": "limit"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # Version miniature du logo blanc
    logo_white_thumbnail = CloudinaryField(
        "client_logo_white_thumbnail",
        resource_type="image",
        folder="clients/logos/white/thumbnails",
        null=True,
        blank=True,
        transformation=[
            {"width": 150, "height": 150, "crop": "fit"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    website = models.URLField(blank=True)
    description = CKEditor5Field("Description", config_name="default", blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(
        default=0, help_text="Ordre d'affichage du client dans la section logos"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Supprimer les images Cloudinary lors de la suppression du client"""
        if self.logo_cloudinary_public_id:
            try:
                cloudinary.uploader.destroy(
                    self.logo_cloudinary_public_id, resource_type="image"
                )
            except Exception as e:
                logger.error(
                    f"Erreur lors de la suppression du logo Cloudinary: {str(e)}"
                )

        if self.logo_white_cloudinary_public_id:
            try:
                cloudinary.uploader.destroy(
                    self.logo_white_cloudinary_public_id, resource_type="image"
                )
            except Exception as e:
                logger.error(
                    f"Erreur lors de la suppression du logo blanc Cloudinary: {str(e)}"
                )
        super().delete(*args, **kwargs)

    @property
    def logo_urls(self):
        """Retourne un dictionnaire avec les URL des différentes versions du logo"""
        urls = {"original": "", "large": "", "thumbnail": ""}

        # URL du logo original
        if hasattr(self, "logo") and self.logo:
            urls["original"] = self.logo.url

        # URL du logo large
        if hasattr(self, "logo_large") and self.logo_large:
            urls["large"] = self.logo_large.url
        elif urls["original"]:
            urls["large"] = urls["original"]

        # URL de la miniature du logo
        if hasattr(self, "logo_thumbnail") and self.logo_thumbnail:
            urls["thumbnail"] = self.logo_thumbnail.url
        elif urls["original"]:
            urls["thumbnail"] = urls["original"]

        return urls

    @property
    def logo_white_urls(self):
        """Retourne un dictionnaire avec les URL des différentes versions du logo blanc"""
        urls = {"original": "", "large": "", "thumbnail": ""}

        # URL du logo blanc original
        if hasattr(self, "logo_white") and self.logo_white:
            urls["original"] = self.logo_white.url

        # URL du logo blanc large
        if hasattr(self, "logo_white_large") and self.logo_white_large:
            urls["large"] = self.logo_white_large.url
        elif urls["original"]:
            urls["large"] = urls["original"]

        # URL de la miniature du logo blanc
        if hasattr(self, "logo_white_thumbnail") and self.logo_white_thumbnail:
            urls["thumbnail"] = self.logo_white_thumbnail.url
        elif urls["original"]:
            urls["thumbnail"] = urls["original"]

        return urls

    def __str__(self):
        return self.name


class ProjectStatus(models.TextChoices):
    """Statuts possibles d'un projet"""

    DRAFT = "draft", "Brouillon"
    IN_PROGRESS = "in_progress", "En cours"
    COMPLETED = "completed", "Terminé"
    ON_HOLD = "on_hold", "En pause"
    CANCELLED = "cancelled", "Annulé"


class Project(models.Model):
    """Modèle principal pour les projets/case studies"""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    subtitle = models.CharField(
        max_length=300, blank=True, help_text="Sous-titre du projet"
    )
    description = models.TextField(help_text="Description courte pour les cartes")
    content = CKEditor5Field(
        "Content",
        config_name="extends",
        blank=True,
        help_text="Contenu détaillé du case study",
    )

    # Relations
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )
    categories = models.ManyToManyField(ProjectCategory, related_name="projects")
    team_members = models.ManyToManyField(
        User, through="ProjectTeamMember", related_name="projects"
    )

    # Images
    # Cloudinary public_id pour référence et suppression
    featured_image_cloudinary_public_id = models.CharField(
        max_length=255, blank=True, default=""
    )

    # Version originale de l'image principale
    featured_image = CloudinaryField(
        "project_featured_image",
        resource_type="image",
        folder="projects/featured/original",
        null=True,
        blank=True,
    )

    # Version pour affichage principal (page de détail)
    featured_image_large = CloudinaryField(
        "project_featured_image_large",
        resource_type="image",
        folder="projects/featured/large",
        null=True,
        blank=True,
        transformation=[
            {"width": 1200, "height": 800, "crop": "fill"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # Version pour les listes/grilles de projets
    thumbnail = CloudinaryField(
        "project_featured_image_thumbnail",
        resource_type="image",
        folder="projects/featured/thumbnails",
        null=True,
        blank=True,
        transformation=[
            {"width": 400, "height": 300, "crop": "fill"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # Métadonnées
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.DRAFT
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # SEO et affichage
    is_featured = models.BooleanField(default=False, help_text="Projet mis en avant")
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ["-order", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def duration_in_days(self):
        """Calcule la durée du projet en jours"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None

    @property
    def category_badges(self):
        """Retourne la liste des catégories pour l'affichage en badges"""
        return self.categories.all()

    @property
    def featured_image_urls(self):
        """Retourne un dictionnaire avec les URL des différentes versions de l'image principale"""
        urls = {"original": "", "large": "", "thumbnail": ""}

        # URL de l'image originale
        if hasattr(self, "featured_image") and self.featured_image:
            urls["original"] = self.featured_image.url

        # URL de l'image large
        if hasattr(self, "featured_image_large") and self.featured_image_large:
            urls["large"] = self.featured_image_large.url
        elif urls["original"]:
            urls["large"] = urls["original"]

        # URL de la vignette
        if hasattr(self, "thumbnail") and self.thumbnail:
            urls["thumbnail"] = self.thumbnail.url
        elif urls["original"]:
            urls["thumbnail"] = urls["original"]

        return urls

    @property
    def featured_image_url(self):
        """Retourne l'URL optimisée de l'image principale (compatibilité)"""
        image_urls = self.featured_image_urls
        return image_urls["large"] or image_urls["original"]

    @property
    def thumbnail_url(self):
        """Retourne l'URL de la miniature (compatibilité)"""
        image_urls = self.featured_image_urls
        return image_urls["thumbnail"] or image_urls["original"]

    def get_gallery_images(self):
        """Retourne toutes les images de la galerie ordonnées"""
        return self.images.all().order_by("order", "created_at")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Supprimer les images Cloudinary lors de la suppression du projet"""
        if self.featured_image_cloudinary_public_id:
            try:
                cloudinary.uploader.destroy(
                    self.featured_image_cloudinary_public_id, resource_type="image"
                )
            except Exception as e:
                logger.error(
                    f"Erreur lors de la suppression de l'image principale Cloudinary: {str(e)}"
                )
        super().delete(*args, **kwargs)

    def generate_image_versions(self):
        """
        Génère les versions optimisées de l'image principale
        """
        if not self.featured_image:
            return False

        try:
            # Générer la version large
            large_result = cloudinary.uploader.upload(
                self.featured_image.url,
                folder="projects/featured/large",
                public_id=f"{self.slug}_large",
                transformation=[
                    {"width": 1200, "height": 800, "crop": "fill"},
                    {"quality": "auto"},
                    {"fetch_format": "auto"},
                ],
                overwrite=True,
            )

            # Générer la version thumbnail
            thumb_result = cloudinary.uploader.upload(
                self.featured_image.url,
                folder="projects/featured/thumbnails",
                public_id=f"{self.slug}_thumb",
                transformation=[
                    {"width": 400, "height": 300, "crop": "fill"},
                    {"quality": "auto"},
                    {"fetch_format": "auto"},
                ],
                overwrite=True,
            )

            # Mettre à jour les champs
            self.featured_image_large = large_result["secure_url"]
            self.thumbnail = thumb_result["secure_url"]

            # Sauvegarder le public_id original si pas déjà fait
            if not self.featured_image_cloudinary_public_id:
                self.featured_image_cloudinary_public_id = self.featured_image.public_id

            self.save(
                update_fields=[
                    "featured_image_large",
                    "thumbnail",
                    "featured_image_cloudinary_public_id",
                ]
            )

            logger.info(f"Versions d'images générées pour: {self.title}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la génération des versions: {str(e)}")
            return False


class ProjectImage(models.Model):
    """Images additionnelles pour un projet"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )

    # Cloudinary public_id pour référence et suppression
    image_cloudinary_public_id = models.CharField(
        max_length=255, blank=True, default=""
    )

    # Version originale de l'image
    image = CloudinaryField(
        "project_gallery_image",
        resource_type="image",
        folder="projects/gallery/original",
        null=True,
        blank=True,
    )

    # Version pour affichage principal
    image_large = CloudinaryField(
        "project_gallery_image_large",
        resource_type="image",
        folder="projects/gallery/large",
        null=True,
        blank=True,
        transformation=[
            {"width": 1200, "height": 800, "crop": "limit"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # Version miniature
    image_thumbnail = CloudinaryField(
        "project_gallery_image_thumbnail",
        resource_type="image",
        folder="projects/gallery/thumbnails",
        null=True,
        blank=True,
        transformation=[
            {"width": 300, "height": 200, "crop": "fill"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    title = models.CharField(max_length=200, blank=True)
    description = CKEditor5Field("Description", config_name="default", blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image de projet"
        verbose_name_plural = "Images de projet"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"

    @property
    def image_urls(self):
        """Retourne un dictionnaire avec les URL des différentes versions de l'image"""
        urls = {"original": "", "large": "", "thumbnail": ""}

        # URL de l'image originale
        if hasattr(self, "image") and self.image:
            urls["original"] = self.image.url

        # URL de l'image large
        if hasattr(self, "image_large") and self.image_large:
            urls["large"] = self.image_large.url
        elif urls["original"]:
            urls["large"] = urls["original"]

        # URL de la vignette
        if hasattr(self, "image_thumbnail") and self.image_thumbnail:
            urls["thumbnail"] = self.image_thumbnail.url
        elif urls["original"]:
            urls["thumbnail"] = urls["original"]

        return urls

    @property
    def image_url(self):
        """Retourne l'URL de l'image (compatibilité)"""
        image_urls = self.image_urls
        return image_urls["large"] or image_urls["original"]

    def get_thumbnail_url(self, width=300, height=200):
        """Génère une URL de miniature avec dimensions personnalisées (compatibilité)"""
        image_urls = self.image_urls
        return image_urls["thumbnail"] or image_urls["original"]

    def delete(self, *args, **kwargs):
        """Supprimer les images Cloudinary lors de la suppression de l'image"""
        if self.image_cloudinary_public_id:
            try:
                cloudinary.uploader.destroy(
                    self.image_cloudinary_public_id, resource_type="image"
                )
            except Exception as e:
                logger.error(
                    f"Erreur lors de la suppression de l'image de galerie Cloudinary: {str(e)}"
                )
        super().delete(*args, **kwargs)


class ProjectTeamMember(models.Model):
    """Relation entre un projet et les membres de l'équipe"""

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=100, help_text="Rôle dans le projet (ex: Designer, Développeur)"
    )
    is_lead = models.BooleanField(default=False, help_text="Chef de projet")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Membre d'équipe"
        verbose_name_plural = "Membres d'équipe"
        unique_together = ["project", "user"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role} ({self.project.title})"


class ProjectTestimonial(models.Model):
    """Témoignages clients pour un projet"""

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="testimonial"
    )
    client_name = models.CharField(max_length=200)
    client_position = models.CharField(max_length=200, blank=True)

    # Cloudinary public_id pour référence et suppression
    client_photo_cloudinary_public_id = models.CharField(
        max_length=255, blank=True, default=""
    )

    # Version originale de la photo client
    client_photo = CloudinaryField(
        "testimonial_client_photo",
        resource_type="image",
        folder="testimonials/original",
        null=True,
        blank=True,
    )

    # Version pour affichage principal
    client_photo_large = CloudinaryField(
        "testimonial_client_photo_large",
        resource_type="image",
        folder="testimonials/large",
        null=True,
        blank=True,
        transformation=[
            {"width": 200, "height": 200, "crop": "fill", "gravity": "face"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # Version miniature
    client_photo_thumbnail = CloudinaryField(
        "testimonial_client_photo_thumbnail",
        resource_type="image",
        folder="testimonials/thumbnails",
        null=True,
        blank=True,
        transformation=[
            {"width": 80, "height": 80, "crop": "fill", "gravity": "face"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    quote = models.TextField()
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)], default=5
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"

    def __str__(self):
        return f"Témoignage de {self.client_name} pour {self.project.title}"

    @property
    def client_photo_urls(self):
        """Retourne un dictionnaire avec les URL des différentes versions de la photo client"""
        urls = {"original": "", "large": "", "thumbnail": ""}

        # URL de la photo originale
        if hasattr(self, "client_photo") and self.client_photo:
            urls["original"] = self.client_photo.url

        # URL de la photo large
        if hasattr(self, "client_photo_large") and self.client_photo_large:
            urls["large"] = self.client_photo_large.url
        elif urls["original"]:
            urls["large"] = urls["original"]

        # URL de la vignette
        if hasattr(self, "client_photo_thumbnail") and self.client_photo_thumbnail:
            urls["thumbnail"] = self.client_photo_thumbnail.url
        elif urls["original"]:
            urls["thumbnail"] = urls["original"]

        return urls

    def delete(self, *args, **kwargs):
        """Supprimer les images Cloudinary lors de la suppression du témoignage"""
        if self.client_photo_cloudinary_public_id:
            try:
                cloudinary.uploader.destroy(
                    self.client_photo_cloudinary_public_id, resource_type="image"
                )
            except Exception as e:
                logger.error(
                    f"Erreur lors de la suppression de la photo client Cloudinary: {str(e)}"
                )
        super().delete(*args, **kwargs)


class ProjectMetrics(models.Model):
    """Métriques et résultats d'un projet"""

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="metrics"
    )

    # Métriques de performance
    page_views_increase = models.FloatField(
        blank=True, null=True, help_text="Augmentation du trafic en %"
    )
    conversion_rate_increase = models.FloatField(
        blank=True, null=True, help_text="Amélioration du taux de conversion en %"
    )
    bounce_rate_decrease = models.FloatField(
        blank=True, null=True, help_text="Réduction du taux de rebond en %"
    )
    loading_time_improvement = models.FloatField(
        blank=True, null=True, help_text="Amélioration du temps de chargement en %"
    )

    # Métriques business
    revenue_increase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Augmentation du chiffre d'affaires",
    )
    leads_increase = models.FloatField(
        blank=True, null=True, help_text="Augmentation des leads en %"
    )

    # Métriques techniques
    seo_score = models.PositiveIntegerField(
        blank=True, null=True, help_text="Score SEO sur 100"
    )
    accessibility_score = models.PositiveIntegerField(
        blank=True, null=True, help_text="Score d'accessibilité sur 100"
    )
    performance_score = models.PositiveIntegerField(
        blank=True, null=True, help_text="Score de performance sur 100"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Métriques de projet"
        verbose_name_plural = "Métriques de projets"

    def __str__(self):
        return f"Métriques pour {self.project.title}"
