from django.core.management.base import BaseCommand
import cloudinary.api
import cloudinary.uploader
from projects.models import Project, ProjectImage, ProjectTestimonial, Client
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Nettoie les images orphelines sur Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les images qui seraient supprimées sans les supprimer'
        )
        parser.add_argument(
            '--folder',
            type=str,
            help='Spécifie un dossier spécifique à nettoyer'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        folder = options['folder']
        
        self.stdout.write(
            self.style.SUCCESS('🧹 Début du nettoyage des images orphelines sur Cloudinary')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  Mode DRY-RUN: Aucune suppression ne sera effectuée')
            )

        folders_to_check = [
            'projects/featured',
            'projects/gallery', 
            'clients/logos',
            'testimonials'
        ] if not folder else [folder]

        for folder_path in folders_to_check:
            self.cleanup_folder(folder_path, dry_run)

        self.stdout.write(
            self.style.SUCCESS('✅ Nettoyage terminé!')
        )

    def cleanup_folder(self, folder_path, dry_run=False):
        """Nettoie un dossier spécifique"""
        self.stdout.write(f'📁 Vérification du dossier: {folder_path}')
        
        try:
            # Récupérer toutes les images du dossier
            resources = cloudinary.api.resources(
                type="upload",
                prefix=folder_path,
                max_results=500
            )
            
            total_images = len(resources['resources'])
            self.stdout.write(f'   {total_images} images trouvées')
            
            if total_images == 0:
                return
            
            # Collecter les public_ids utilisés dans la base de données
            used_public_ids = set()
            
            # Projects
            for project in Project.objects.all():
                if project.featured_image_cloudinary_public_id:
                    used_public_ids.add(project.featured_image_cloudinary_public_id)
                    used_public_ids.add(f"{project.slug}_large")
                    used_public_ids.add(f"{project.slug}_thumb")
            
            # Project Images
            for img in ProjectImage.objects.all():
                if img.image_cloudinary_public_id:
                    used_public_ids.add(img.image_cloudinary_public_id)
                    used_public_ids.add(f"{img.project.slug}_gallery_{img.id}_large")
                    used_public_ids.add(f"{img.project.slug}_gallery_{img.id}_thumb")
            
            # Clients
            for client in Client.objects.all():
                if client.logo_cloudinary_public_id:
                    used_public_ids.add(client.logo_cloudinary_public_id)
                    used_public_ids.add(f"{client.slug}_logo_large")
                    used_public_ids.add(f"{client.slug}_logo_thumb")
                
                if client.logo_white_cloudinary_public_id:
                    used_public_ids.add(client.logo_white_cloudinary_public_id)
                    used_public_ids.add(f"{client.slug}_logo_white_large")
                    used_public_ids.add(f"{client.slug}_logo_white_thumb")
            
            # Testimonials
            for testimonial in ProjectTestimonial.objects.all():
                if testimonial.client_photo_cloudinary_public_id:
                    used_public_ids.add(testimonial.client_photo_cloudinary_public_id)
                    used_public_ids.add(f"{testimonial.project.slug}_testimonial_large")
                    used_public_ids.add(f"{testimonial.project.slug}_testimonial_thumb")
            
            # Identifier les images orphelines
            orphaned_images = []
            for resource in resources['resources']:
                public_id = resource['public_id']
                if public_id not in used_public_ids:
                    orphaned_images.append(public_id)
            
            orphaned_count = len(orphaned_images)
            self.stdout.write(f'   {orphaned_count} images orphelines trouvées')
            
            if orphaned_count == 0:
                return
            
            # Afficher ou supprimer les images orphelines
            for i, public_id in enumerate(orphaned_images, 1):
                if dry_run:
                    self.stdout.write(f'   🗑️  [{i}/{orphaned_count}] SERAIT SUPPRIMÉ: {public_id}')
                else:
                    try:
                        cloudinary.uploader.destroy(public_id, resource_type="image")
                        self.stdout.write(f'   ✅ [{i}/{orphaned_count}] SUPPRIMÉ: {public_id}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'   ❌ [{i}/{orphaned_count}] ERREUR pour {public_id}: {str(e)}')
                        )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors du nettoyage du dossier {folder_path}: {str(e)}')
            )
