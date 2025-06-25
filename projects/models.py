from django.db import models
from django.utils.text import slugify
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from cloudinary.models import CloudinaryField

# from django.contrib.auth.models import User
# Importing User model from Django settings to ensure compatibility with custom user models
# from django settings import AUTH_USER_MODEL
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ProjectCategory(models.Model):
    """Catégorie de projet (ex: Branding, UI/UX, Development, etc.)"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
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
    logo = CloudinaryField(
        "image",
        folder="clients/logos",
        blank=True,
        null=True,
        help_text="Logo du client (upload automatique vers Cloudinary)",
    )
    logo_white = CloudinaryField(
        "image",
        folder="clients/logos/white",
        blank=True,
        null=True,
        help_text="Version blanche du logo (upload automatique vers Cloudinary)",
    )
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
    content = models.TextField(blank=True, help_text="Contenu détaillé du case study")

    # Relations
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )
    categories = models.ManyToManyField(ProjectCategory, related_name="projects")
    team_members = models.ManyToManyField(
        User, through="ProjectTeamMember", related_name="projects"
    )

    # Images
    featured_image = CloudinaryField(
        "image",
        folder="projects/featured",
        help_text="Image principale du projet (upload automatique vers Cloudinary)",
        transformation={
            "quality": "auto",
            "fetch_format": "auto",
            "width": 1200,
            "height": 800,
            "crop": "fill",
        },
    )
    thumbnail = CloudinaryField(
        "image",
        folder="projects/thumbnails",
        blank=True,
        null=True,
        help_text="Miniature du projet (générée automatiquement si vide)",
        transformation={
            "quality": "auto",
            "fetch_format": "auto",
            "width": 400,
            "height": 300,
            "crop": "fill",
        },
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
    def featured_image_url(self):
        """Retourne l'URL optimisée de l'image principale"""
        if self.featured_image:
            return str(self.featured_image)
        return None

    @property
    def thumbnail_url(self):
        """Retourne l'URL de la miniature ou génère une miniature depuis l'image principale"""
        if self.thumbnail:
            return str(self.thumbnail)
        elif self.featured_image:
            # Génère automatiquement une miniature depuis l'image principale
            from cloudinary import CloudinaryImage

            return CloudinaryImage(str(self.featured_image)).build_url(
                width=400, height=300, crop="fill", quality="auto", fetch_format="auto"
            )
        return None

    def get_gallery_images(self):
        """Retourne toutes les images de la galerie ordonnées"""
        return self.images.all().order_by("order", "created_at")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-génération de la miniature si elle n'existe pas
        if self.featured_image and not self.thumbnail:
            self.thumbnail = self.featured_image

        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    """Images additionnelles pour un projet"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = CloudinaryField(
        "image",
        folder="projects/gallery",
        help_text="Image de galerie (upload automatique vers Cloudinary)",
        transformation={
            "quality": "auto",
            "fetch_format": "auto",
            "width": 1200,
            "height": 800,
            "crop": "limit",
        },
    )
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image de projet"
        verbose_name_plural = "Images de projet"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"

    @property
    def image_url(self):
        """Retourne l'URL de l'image"""
        if self.image:
            return str(self.image)
        return None

    def get_thumbnail_url(self, width=300, height=200):
        """Génère une URL de miniature avec dimensions personnalisées"""
        if self.image:
            from cloudinary import CloudinaryImage

            return CloudinaryImage(str(self.image)).build_url(
                width=width,
                height=height,
                crop="fill",
                quality="auto",
                fetch_format="auto",
            )
        return None


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
    client_photo = CloudinaryField(
        "image",
        folder="testimonials",
        blank=True,
        null=True,
        help_text="Photo du client (upload automatique vers Cloudinary)",
        transformation={
            "quality": "auto",
            "fetch_format": "auto",
            "width": 150,
            "height": 150,
            "crop": "fill",
            "gravity": "face",
        },
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
