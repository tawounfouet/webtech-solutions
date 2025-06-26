from django.core.management.base import BaseCommand
from django.db import transaction
from projects.models import Project, ProjectImage, ProjectTestimonial, Client
import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Génère les versions optimisées pour toutes les images existantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['project', 'client', 'testimonial', 'projectimage', 'all'],
            default='all',
            help='Spécifie quel modèle traiter (default: all)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la régénération même si les versions existent déjà'
        )

    def handle(self, *args, **options):
        model_choice = options['model']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Début de la génération des versions d\'images pour: {model_choice}')
        )

        if model_choice in ['project', 'all']:
            self.generate_project_images(force)
        
        if model_choice in ['client', 'all']:
            self.generate_client_images(force)
        
        if model_choice in ['testimonial', 'all']:
            self.generate_testimonial_images(force)
        
        if model_choice in ['projectimage', 'all']:
            self.generate_project_gallery_images(force)

        self.stdout.write(
            self.style.SUCCESS('✅ Génération des versions d\'images terminée!')
        )

    def generate_project_images(self, force=False):
        """Génère les versions pour les images principales des projets"""
        self.stdout.write('📸 Traitement des images principales des projets...')
        
        projects = Project.objects.filter(featured_image__isnull=False)
        if not force:
            projects = projects.filter(featured_image_large__isnull=True)
        
        total = projects.count()
        self.stdout.write(f'   {total} projets à traiter')
        
        for i, project in enumerate(projects, 1):
            try:
                with transaction.atomic():
                    if project.featured_image:
                        # Générer la version large
                        large_result = cloudinary.uploader.upload(
                            project.featured_image.url,
                            folder="projects/featured/large",
                            public_id=f"{project.slug}_large",
                            transformation=[
                                {"width": 1200, "height": 800, "crop": "fill"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        # Générer la version thumbnail
                        thumb_result = cloudinary.uploader.upload(
                            project.featured_image.url,
                            folder="projects/featured/thumbnails",
                            public_id=f"{project.slug}_thumb",
                            transformation=[
                                {"width": 400, "height": 300, "crop": "fill"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        # Mettre à jour les champs
                        project.featured_image_large = large_result['secure_url']
                        project.thumbnail = thumb_result['secure_url']
                        
                        if not project.featured_image_cloudinary_public_id:
                            project.featured_image_cloudinary_public_id = project.featured_image.public_id
                        
                        project.save(update_fields=[
                            'featured_image_large', 
                            'thumbnail', 
                            'featured_image_cloudinary_public_id'
                        ])
                        
                        self.stdout.write(f'   ✅ [{i}/{total}] {project.title}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ [{i}/{total}] Erreur pour {project.title}: {str(e)}')
                )

    def generate_client_images(self, force=False):
        """Génère les versions pour les logos des clients"""
        self.stdout.write('🏢 Traitement des logos des clients...')
        
        # Logos principaux
        clients = Client.objects.filter(logo__isnull=False)
        if not force:
            clients = clients.filter(logo_large__isnull=True)
        
        total = clients.count()
        self.stdout.write(f'   {total} logos principaux à traiter')
        
        for i, client in enumerate(clients, 1):
            try:
                with transaction.atomic():
                    if client.logo:
                        # Générer la version large
                        large_result = cloudinary.uploader.upload(
                            client.logo.url,
                            folder="clients/logos/large",
                            public_id=f"{client.slug}_logo_large",
                            transformation=[
                                {"width": 400, "crop": "limit"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        # Générer la version thumbnail
                        thumb_result = cloudinary.uploader.upload(
                            client.logo.url,
                            folder="clients/logos/thumbnails",
                            public_id=f"{client.slug}_logo_thumb",
                            transformation=[
                                {"width": 150, "height": 150, "crop": "fit"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        client.logo_large = large_result['secure_url']
                        client.logo_thumbnail = thumb_result['secure_url']
                        
                        if not client.logo_cloudinary_public_id:
                            client.logo_cloudinary_public_id = client.logo.public_id
                        
                        client.save(update_fields=[
                            'logo_large', 
                            'logo_thumbnail', 
                            'logo_cloudinary_public_id'
                        ])
                        
                        self.stdout.write(f'   ✅ [{i}/{total}] Logo principal: {client.name}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ [{i}/{total}] Erreur logo principal {client.name}: {str(e)}')
                )
        
        # Logos blancs
        clients_white = Client.objects.filter(logo_white__isnull=False)
        if not force:
            clients_white = clients_white.filter(logo_white_large__isnull=True)
        
        total_white = clients_white.count()
        self.stdout.write(f'   {total_white} logos blancs à traiter')
        
        for i, client in enumerate(clients_white, 1):
            try:
                with transaction.atomic():
                    if client.logo_white:
                        # Générer la version large
                        large_result = cloudinary.uploader.upload(
                            client.logo_white.url,
                            folder="clients/logos/white/large",
                            public_id=f"{client.slug}_logo_white_large",
                            transformation=[
                                {"width": 400, "crop": "limit"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        # Générer la version thumbnail
                        thumb_result = cloudinary.uploader.upload(
                            client.logo_white.url,
                            folder="clients/logos/white/thumbnails",
                            public_id=f"{client.slug}_logo_white_thumb",
                            transformation=[
                                {"width": 150, "height": 150, "crop": "fit"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        client.logo_white_large = large_result['secure_url']
                        client.logo_white_thumbnail = thumb_result['secure_url']
                        
                        if not client.logo_white_cloudinary_public_id:
                            client.logo_white_cloudinary_public_id = client.logo_white.public_id
                        
                        client.save(update_fields=[
                            'logo_white_large', 
                            'logo_white_thumbnail', 
                            'logo_white_cloudinary_public_id'
                        ])
                        
                        self.stdout.write(f'   ✅ [{i}/{total_white}] Logo blanc: {client.name}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ [{i}/{total_white}] Erreur logo blanc {client.name}: {str(e)}')
                )

    def generate_testimonial_images(self, force=False):
        """Génère les versions pour les photos des témoignages"""
        self.stdout.write('💬 Traitement des photos des témoignages...')
        
        testimonials = ProjectTestimonial.objects.filter(client_photo__isnull=False)
        if not force:
            testimonials = testimonials.filter(client_photo_large__isnull=True)
        
        total = testimonials.count()
        self.stdout.write(f'   {total} photos de témoignages à traiter')
        
        for i, testimonial in enumerate(testimonials, 1):
            try:
                with transaction.atomic():
                    if testimonial.client_photo:
                        # Générer la version large
                        large_result = cloudinary.uploader.upload(
                            testimonial.client_photo.url,
                            folder="testimonials/large",
                            public_id=f"{testimonial.project.slug}_testimonial_large",
                            transformation=[
                                {"width": 200, "height": 200, "crop": "fill", "gravity": "face"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        # Générer la version thumbnail
                        thumb_result = cloudinary.uploader.upload(
                            testimonial.client_photo.url,
                            folder="testimonials/thumbnails",
                            public_id=f"{testimonial.project.slug}_testimonial_thumb",
                            transformation=[
                                {"width": 80, "height": 80, "crop": "fill", "gravity": "face"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        testimonial.client_photo_large = large_result['secure_url']
                        testimonial.client_photo_thumbnail = thumb_result['secure_url']
                        
                        if not testimonial.client_photo_cloudinary_public_id:
                            testimonial.client_photo_cloudinary_public_id = testimonial.client_photo.public_id
                        
                        testimonial.save(update_fields=[
                            'client_photo_large', 
                            'client_photo_thumbnail', 
                            'client_photo_cloudinary_public_id'
                        ])
                        
                        self.stdout.write(f'   ✅ [{i}/{total}] {testimonial.project.title}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ [{i}/{total}] Erreur pour {testimonial.project.title}: {str(e)}')
                )

    def generate_project_gallery_images(self, force=False):
        """Génère les versions pour les images de galerie des projets"""
        self.stdout.write('🖼️  Traitement des images de galerie...')
        
        images = ProjectImage.objects.filter(image__isnull=False)
        if not force:
            images = images.filter(image_large__isnull=True)
        
        total = images.count()
        self.stdout.write(f'   {total} images de galerie à traiter')
        
        for i, image in enumerate(images, 1):
            try:
                with transaction.atomic():
                    if image.image:
                        # Générer la version large
                        large_result = cloudinary.uploader.upload(
                            image.image.url,
                            folder="projects/gallery/large",
                            public_id=f"{image.project.slug}_gallery_{image.id}_large",
                            transformation=[
                                {"width": 1200, "height": 800, "crop": "limit"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        # Générer la version thumbnail
                        thumb_result = cloudinary.uploader.upload(
                            image.image.url,
                            folder="projects/gallery/thumbnails",
                            public_id=f"{image.project.slug}_gallery_{image.id}_thumb",
                            transformation=[
                                {"width": 300, "height": 200, "crop": "fill"},
                                {"quality": "auto"},
                                {"fetch_format": "auto"},
                            ],
                            overwrite=True
                        )
                        
                        image.image_large = large_result['secure_url']
                        image.image_thumbnail = thumb_result['secure_url']
                        
                        if not image.image_cloudinary_public_id:
                            image.image_cloudinary_public_id = image.image.public_id
                        
                        image.save(update_fields=[
                            'image_large', 
                            'image_thumbnail', 
                            'image_cloudinary_public_id'
                        ])
                        
                        self.stdout.write(f'   ✅ [{i}/{total}] {image.project.title} - Image {image.order}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ [{i}/{total}] Erreur pour {image.project.title}: {str(e)}')
                )
