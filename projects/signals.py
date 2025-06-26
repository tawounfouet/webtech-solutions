from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Project, ProjectImage, ProjectTestimonial, Client
import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)


def generate_image_versions(original_field, large_field_name, thumb_field_name, instance, 
                          large_folder, thumb_folder, large_transform, thumb_transform, 
                          public_id_field, identifier):
    """
    Fonction utilitaire pour générer les versions d'images
    """    
    if not original_field:
        return False
    
    # Vérifier si les versions existent déjà
    large_field_value = getattr(instance, large_field_name, None)
    if large_field_value:
        return False
    
    try:        
        # Générer la version large
        large_result = cloudinary.uploader.upload(
            original_field.url,
            folder=large_folder,
            public_id=f"{identifier}_large",
            transformation=large_transform,
            overwrite=True
        )
        
        # Générer la version thumbnail
        thumb_result = cloudinary.uploader.upload(
            original_field.url,
            folder=thumb_folder,
            public_id=f"{identifier}_thumb",
            transformation=thumb_transform,
            overwrite=True
        )
        
        # Mettre à jour les champs
        setattr(instance, large_field_name, large_result['secure_url'])
        setattr(instance, thumb_field_name, thumb_result['secure_url'])
        
        # Sauvegarder le public_id original si pas déjà fait
        if hasattr(instance, public_id_field) and not getattr(instance, public_id_field):
            setattr(instance, public_id_field, original_field.public_id)
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des versions d'images pour {identifier}: {str(e)}")
        return False


# ===============================
# SIGNAUX POUR LE MODÈLE PROJECT
# ===============================

@receiver(post_save, sender=Project)
def generate_project_featured_image_versions(sender, instance, created, **kwargs):
    """
    Génère automatiquement les versions optimisées de l'image principale du projet
    """
    if instance.featured_image and not instance.featured_image_large:        
        success = generate_image_versions(
            original_field=instance.featured_image,
            large_field_name="featured_image_large",
            thumb_field_name="thumbnail",
            instance=instance,
            large_folder="projects/featured/large",
            thumb_folder="projects/featured/thumbnails",
            large_transform=[
                {"width": 1200, "height": 800, "crop": "fill"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            thumb_transform=[
                {"width": 400, "height": 300, "crop": "fill"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            public_id_field="featured_image_cloudinary_public_id",
            identifier=instance.slug
        )
        
        if success:
            # Sauvegarder sans déclencher le signal à nouveau
            Project.objects.filter(pk=instance.pk).update(
                featured_image_large=instance.featured_image_large,
                thumbnail=instance.thumbnail,
                featured_image_cloudinary_public_id=instance.featured_image_cloudinary_public_id
            )
            logger.info(f"Versions d'images générées pour le projet: {instance.title}")
        else:
            logger.error(f"Échec de la génération des versions pour: {instance.title}")


@receiver(pre_delete, sender=Project)
def cleanup_project_images(sender, instance, **kwargs):
    """
    Nettoie toutes les versions d'images Cloudinary du projet avant suppression
    """
    public_ids_to_delete = []
    
    if instance.featured_image_cloudinary_public_id:
        public_ids_to_delete.append(instance.featured_image_cloudinary_public_id)
        public_ids_to_delete.append(f"{instance.slug}_large")
        public_ids_to_delete.append(f"{instance.slug}_thumb")
    
    for public_id in public_ids_to_delete:
        try:
            cloudinary.uploader.destroy(public_id, resource_type="image")
            logger.info(f"Image Cloudinary supprimée: {public_id}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'image {public_id}: {str(e)}")


# ===================================
# SIGNAUX POUR LE MODÈLE PROJECT IMAGE
# ===================================

@receiver(post_save, sender=ProjectImage)
def generate_project_image_versions(sender, instance, created, **kwargs):
    """
    Génère automatiquement les versions optimisées des images de galerie
    """
    if instance.image and not instance.image_large:
        success = generate_image_versions(
            original_field=instance.image,
            large_field_name="image_large",
            thumb_field_name="image_thumbnail",
            instance=instance,
            large_folder="projects/gallery/large",
            thumb_folder="projects/gallery/thumbnails",
            large_transform=[
                {"width": 1200, "height": 800, "crop": "limit"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            thumb_transform=[
                {"width": 300, "height": 200, "crop": "fill"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            public_id_field="image_cloudinary_public_id",
            identifier=f"{instance.project.slug}_gallery_{instance.id}"
        )
        
        if success:
            # Sauvegarder sans déclencher le signal à nouveau
            ProjectImage.objects.filter(pk=instance.pk).update(
                image_large=instance.image_large,
                image_thumbnail=instance.image_thumbnail,
                image_cloudinary_public_id=instance.image_cloudinary_public_id
            )
            logger.info(f"Versions d'images générées pour l'image de galerie: {instance.project.title}")


@receiver(pre_delete, sender=ProjectImage)
def cleanup_project_image(sender, instance, **kwargs):
    """
    Nettoie toutes les versions d'images Cloudinary de l'image de galerie avant suppression
    """
    public_ids_to_delete = []
    
    if instance.image_cloudinary_public_id:
        identifier = f"{instance.project.slug}_gallery_{instance.id}"
        public_ids_to_delete.append(instance.image_cloudinary_public_id)
        public_ids_to_delete.append(f"{identifier}_large")
        public_ids_to_delete.append(f"{identifier}_thumb")
    
    for public_id in public_ids_to_delete:
        try:
            cloudinary.uploader.destroy(public_id, resource_type="image")
            logger.info(f"Image Cloudinary supprimée: {public_id}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'image {public_id}: {str(e)}")


# =====================================
# SIGNAUX POUR LE MODÈLE CLIENT
# =====================================

@receiver(post_save, sender=Client)
def generate_client_logo_versions(sender, instance, created, **kwargs):
    """
    Génère automatiquement les versions optimisées des logos client
    """
    # Générer les versions du logo principal
    if instance.logo and not instance.logo_large:
        success = generate_image_versions(
            original_field=instance.logo,
            large_field_name="logo_large",
            thumb_field_name="logo_thumbnail",
            instance=instance,
            large_folder="clients/logos/large",
            thumb_folder="clients/logos/thumbnails",
            large_transform=[
                {"width": 400, "crop": "limit"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            thumb_transform=[
                {"width": 150, "height": 150, "crop": "fit"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            public_id_field="logo_cloudinary_public_id",
            identifier=f"{instance.slug}_logo"
        )
        
        if success:
            Client.objects.filter(pk=instance.pk).update(
                logo_large=instance.logo_large,
                logo_thumbnail=instance.logo_thumbnail,
                logo_cloudinary_public_id=instance.logo_cloudinary_public_id
            )
            logger.info(f"Versions du logo générées pour le client: {instance.name}")
    
    # Générer les versions du logo blanc
    if instance.logo_white and not instance.logo_white_large:
        success = generate_image_versions(
            original_field=instance.logo_white,
            large_field_name="logo_white_large",
            thumb_field_name="logo_white_thumbnail",
            instance=instance,
            large_folder="clients/logos/white/large",
            thumb_folder="clients/logos/white/thumbnails",
            large_transform=[
                {"width": 400, "crop": "limit"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            thumb_transform=[
                {"width": 150, "height": 150, "crop": "fit"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            public_id_field="logo_white_cloudinary_public_id",
            identifier=f"{instance.slug}_logo_white"
        )
        
        if success:
            Client.objects.filter(pk=instance.pk).update(
                logo_white_large=instance.logo_white_large,
                logo_white_thumbnail=instance.logo_white_thumbnail,
                logo_white_cloudinary_public_id=instance.logo_white_cloudinary_public_id
            )
            logger.info(f"Versions du logo blanc générées pour le client: {instance.name}")


@receiver(pre_delete, sender=Client)
def cleanup_client_images(sender, instance, **kwargs):
    """
    Nettoie toutes les versions d'images Cloudinary du client avant suppression
    """
    public_ids_to_delete = []
    
    # Logos principaux
    if instance.logo_cloudinary_public_id:
        public_ids_to_delete.extend([
            instance.logo_cloudinary_public_id,
            f"{instance.slug}_logo_large",
            f"{instance.slug}_logo_thumb"
        ])
    
    # Logos blancs
    if instance.logo_white_cloudinary_public_id:
        public_ids_to_delete.extend([
            instance.logo_white_cloudinary_public_id,
            f"{instance.slug}_logo_white_large",
            f"{instance.slug}_logo_white_thumb"
        ])
    
    for public_id in public_ids_to_delete:
        try:
            cloudinary.uploader.destroy(public_id, resource_type="image")
            logger.info(f"Image Cloudinary supprimée: {public_id}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'image {public_id}: {str(e)}")


# ==========================================
# SIGNAUX POUR LE MODÈLE PROJECT TESTIMONIAL
# ==========================================

@receiver(post_save, sender=ProjectTestimonial)
def generate_testimonial_photo_versions(sender, instance, created, **kwargs):
    """
    Génère automatiquement les versions optimisées de la photo client du témoignage
    """
    if instance.client_photo and not instance.client_photo_large:
        success = generate_image_versions(
            original_field=instance.client_photo,
            large_field_name="client_photo_large",
            thumb_field_name="client_photo_thumbnail",
            instance=instance,
            large_folder="testimonials/large",
            thumb_folder="testimonials/thumbnails",
            large_transform=[
                {"width": 200, "height": 200, "crop": "fill", "gravity": "face"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            thumb_transform=[
                {"width": 80, "height": 80, "crop": "fill", "gravity": "face"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
            public_id_field="client_photo_cloudinary_public_id",
            identifier=f"{instance.project.slug}_testimonial"
        )
        
        if success:
            ProjectTestimonial.objects.filter(pk=instance.pk).update(
                client_photo_large=instance.client_photo_large,
                client_photo_thumbnail=instance.client_photo_thumbnail,
                client_photo_cloudinary_public_id=instance.client_photo_cloudinary_public_id
            )
            logger.info(f"Versions de la photo client générées pour le témoignage: {instance.project.title}")


@receiver(pre_delete, sender=ProjectTestimonial)
def cleanup_testimonial_images(sender, instance, **kwargs):
    """
    Nettoie toutes les versions d'images Cloudinary du témoignage avant suppression
    """
    public_ids_to_delete = []
    
    if instance.client_photo_cloudinary_public_id:
        identifier = f"{instance.project.slug}_testimonial"
        public_ids_to_delete.extend([
            instance.client_photo_cloudinary_public_id,
            f"{identifier}_large",
            f"{identifier}_thumb"
        ])
    
    for public_id in public_ids_to_delete:
        try:
            cloudinary.uploader.destroy(public_id, resource_type="image")
            logger.info(f"Image Cloudinary supprimée: {public_id}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'image {public_id}: {str(e)}")
