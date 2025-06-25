"""
Utilitaires pour la gestion des images avec Cloudinary
"""

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cloudinary.uploader
import cloudinary
from cloudinary import CloudinaryImage
import os


def generate_responsive_urls(public_id, transformations=None):
    """
    Génère des URLs responsives pour différentes tailles d'écran

    Args:
        public_id (str): L'ID public de l'image sur Cloudinary
        transformations (dict): Transformations personnalisées à appliquer

    Returns:
        dict: URLs pour différentes tailles (small, medium, large)
    """
    if not public_id:
        return {"small": "", "medium": "", "large": ""}

    base_transformations = transformations or {}

    try:
        # URLs pour différentes tailles
        urls = {
            "small": CloudinaryImage(public_id).build_url(
                width=400,
                crop="scale",
                format="auto",
                quality="auto",
                **base_transformations,
            ),
            "medium": CloudinaryImage(public_id).build_url(
                width=800,
                crop="scale",
                format="auto",
                quality="auto",
                **base_transformations,
            ),
            "large": CloudinaryImage(public_id).build_url(
                width=1200,
                crop="scale",
                format="auto",
                quality="auto",
                **base_transformations,
            ),
        }

        return urls
    except Exception:
        return {"small": "", "medium": "", "large": ""}


def get_optimized_image_url(
    public_id, width=None, height=None, crop="fill", quality="auto", format="auto"
):
    """
    Génère une URL optimisée pour une image Cloudinary

    Args:
        public_id (str): L'ID public de l'image
        width (int): Largeur souhaitée
        height (int): Hauteur souhaitée
        crop (str): Mode de recadrage
        quality (str): Qualité de l'image
        format (str): Format de l'image

    Returns:
        str: URL optimisée ou chaîne vide si erreur
    """
    if not public_id:
        return ""

    try:
        transformation_params = {"format": format, "quality": quality}

        if width:
            transformation_params["width"] = width
        if height:
            transformation_params["height"] = height
        if width and height:
            transformation_params["crop"] = crop

        return CloudinaryImage(public_id).build_url(**transformation_params)
    except Exception:
        return ""


def get_thumbnail_url(public_id, size=150):
    """
    Génère une URL pour une miniature carrée

    Args:
        public_id (str): L'ID public de l'image
        size (int): Taille de la miniature (largeur et hauteur)

    Returns:
        str: URL de la miniature
    """
    return get_optimized_image_url(public_id, width=size, height=size, crop="fill")


# Constantes pour les transformations communes
TRANSFORMATIONS = {
    "thumbnail": {"width": 150, "height": 150, "crop": "fill"},
    "small": {"width": 400, "crop": "scale"},
    "medium": {"width": 800, "crop": "scale"},
    "large": {"width": 1200, "crop": "scale"},
    "hero": {"width": 1200, "height": 600, "crop": "fill"},
    "card": {"width": 400, "height": 300, "crop": "fill"},
    "avatar": {"width": 100, "height": 100, "crop": "fill", "gravity": "face"},
    "logo": {"height": 50, "crop": "fit"},
}


class CloudinaryImageField:
    """Classe utilitaire pour gérer les images Cloudinary dans les modèles"""

    @staticmethod
    def upload_image(image_file, folder=None, public_id=None):
        """
        Upload une image vers Cloudinary

        Args:
            image_file: Fichier image Django
            folder: Dossier de destination sur Cloudinary
            public_id: ID public personnalisé

        Returns:
            str: Public ID de l'image uploadée
        """
        upload_options = {
            "resource_type": "image",
            "fetch_format": "auto",  # Optimise automatiquement le format
            "quality": "auto",  # Optimise automatiquement la qualité
        }

        if folder:
            upload_options["folder"] = folder
        if public_id:
            upload_options["public_id"] = public_id

        try:
            result = cloudinary.uploader.upload(image_file, **upload_options)
            return result.get("public_id")
        except Exception as e:
            print(f"Erreur lors de l'upload vers Cloudinary: {e}")
            return None

    @staticmethod
    def delete_image(public_id):
        """
        Supprime une image de Cloudinary

        Args:
            public_id: ID public de l'image à supprimer

        Returns:
            bool: True si la suppression a réussi
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            print(f"Erreur lors de la suppression sur Cloudinary: {e}")
            return False

    @staticmethod
    def get_image_url(public_id, **transformations):
        """
        Génère une URL pour une image Cloudinary

        Args:
            public_id: ID public de l'image
            **transformations: Transformations à appliquer

        Returns:
            str: URL de l'image
        """
        if not public_id:
            return ""

        try:
            from cloudinary import CloudinaryImage

            return CloudinaryImage(public_id).build_url(**transformations)
        except Exception:
            return ""


def optimize_image_for_web(public_id):
    """
    Applique des optimisations standard pour le web

    Args:
        public_id: ID public de l'image

    Returns:
        str: URL de l'image optimisée
    """
    return CloudinaryImageField.get_image_url(
        public_id, format="auto", quality="auto", fetch_format="auto"
    )


def generate_responsive_urls(public_id, sizes=None):
    """
    Génère des URLs pour différentes tailles d'écran

    Args:
        public_id: ID public de l'image
        sizes: Dict des tailles à générer

    Returns:
        dict: URLs pour chaque taille
    """
    if sizes is None:
        sizes = {
            "thumbnail": {"width": 150, "height": 150, "crop": "fill"},
            "small": {"width": 400, "crop": "scale"},
            "medium": {"width": 800, "crop": "scale"},
            "large": {"width": 1200, "crop": "scale"},
            "hero": {"width": 1920, "height": 1080, "crop": "fill"},
        }

    urls = {}
    for size_name, transformations in sizes.items():
        urls[size_name] = CloudinaryImageField.get_image_url(
            public_id, **transformations
        )

    return urls
