"""
Configuration Cloudinary pour Django
"""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings


def configure_cloudinary():
    """Configure Cloudinary avec les variables d'environnement"""
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def get_cloudinary_url(public_id, transformation=None):
    """
    Génère une URL Cloudinary avec transformations optionnelles

    Args:
        public_id (str): ID public de l'image sur Cloudinary
        transformation (dict): Transformations à appliquer (ex: {'width': 300, 'height': 200, 'crop': 'fill'})

    Returns:
        str: URL complète de l'image
    """
    if transformation:
        return cloudinary.CloudinaryImage(public_id).build_url(**transformation)
    return cloudinary.CloudinaryImage(public_id).build_url()


def upload_image(file, folder=None, public_id=None, transformation=None):
    """
    Upload une image vers Cloudinary

    Args:
        file: Fichier à uploader
        folder (str): Dossier de destination sur Cloudinary
        public_id (str): ID public personnalisé
        transformation (dict): Transformations à appliquer lors de l'upload

    Returns:
        dict: Réponse de Cloudinary avec les détails de l'upload
    """
    upload_options = {}

    if folder:
        upload_options["folder"] = folder
    if public_id:
        upload_options["public_id"] = public_id
    if transformation:
        upload_options["transformation"] = transformation

    return cloudinary.uploader.upload(file, **upload_options)


def delete_image(public_id):
    """
    Supprime une image de Cloudinary

    Args:
        public_id (str): ID public de l'image à supprimer

    Returns:
        dict: Réponse de Cloudinary
    """
    return cloudinary.uploader.destroy(public_id)


# Transformations communes
TRANSFORMATIONS = {
    "thumbnail": {"width": 150, "height": 150, "crop": "fill"},
    "medium": {"width": 400, "height": 300, "crop": "fit"},
    "large": {"width": 800, "height": 600, "crop": "fit"},
    "hero": {"width": 1200, "height": 600, "crop": "fill"},
    "avatar": {"width": 100, "height": 100, "crop": "fill", "gravity": "face"},
}
