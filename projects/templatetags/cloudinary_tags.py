"""
Template tags personnalisés pour Cloudinary
"""

from django import template
from django.utils.safestring import mark_safe
import cloudinary
from cloudinary import CloudinaryImage

register = template.Library()


@register.simple_tag
def cloudinary_url(public_id, **kwargs):
    """
    Génère une URL Cloudinary avec transformations

    Usage:
    {% cloudinary_url "sample" width=300 height=200 crop="fill" %}
    """
    if not public_id:
        return ""

    # Convertir les paramètres en transformations Cloudinary
    transformation = {}
    for key, value in kwargs.items():
        transformation[key] = value

    try:
        return CloudinaryImage(public_id).build_url(**transformation)
    except Exception:
        return ""


@register.simple_tag
def cloudinary_image(public_id, alt="", css_class="", **kwargs):
    """
    Génère une balise img complète avec URL Cloudinary

    Usage:
    {% cloudinary_image "sample" alt="Mon image" css_class="img-fluid" width=300 height=200 crop="fill" %}
    """
    if not public_id:
        return ""

    # Séparer les attributs HTML des transformations Cloudinary
    html_attrs = {
        "alt": alt,
        "class": css_class,
    }

    # Les transformations sont tous les autres paramètres
    transformation = {}
    for key, value in kwargs.items():
        if key not in ["alt", "css_class"]:
            transformation[key] = value

    try:
        url = CloudinaryImage(public_id).build_url(**transformation)

        # Construire la balise img
        attrs = []
        for key, value in html_attrs.items():
            if value:  # Seulement si la valeur n'est pas vide
                attrs.append(f'{key}="{value}"')

        attrs_str = " ".join(attrs)
        img_tag = f'<img src="{url}" {attrs_str}>'

        return mark_safe(img_tag)
    except Exception:
        return ""


@register.filter
def cloudinary_thumbnail(public_id, size="150x150"):
    """
    Filtre pour générer des miniatures

    Usage:
    {{ project.featured_image|cloudinary_thumbnail:"300x200" }}
    """
    if not public_id:
        return ""

    try:
        width, height = size.split("x")
        return CloudinaryImage(public_id).build_url(
            width=int(width), height=int(height), crop="fill"
        )
    except Exception:
        return ""


@register.inclusion_tag("cloudinary/responsive_image.html")
def responsive_cloudinary_image(public_id, alt="", css_class="img-fluid"):
    """
    Template tag pour images responsives avec plusieurs tailles

    Usage:
    {% responsive_cloudinary_image "sample" alt="Mon image" css_class="img-fluid" %}
    """
    if not public_id:
        return {"image_url": "", "alt": alt, "css_class": css_class}

    try:
        # Générer différentes tailles pour le responsive
        sizes = {
            "small": CloudinaryImage(public_id).build_url(width=400, crop="scale"),
            "medium": CloudinaryImage(public_id).build_url(width=800, crop="scale"),
            "large": CloudinaryImage(public_id).build_url(width=1200, crop="scale"),
        }

        return {
            "sizes": sizes,
            "image_url": sizes["medium"],  # Image par défaut
            "alt": alt,
            "css_class": css_class,
            "public_id": public_id,
        }
    except Exception:
        return {"image_url": "", "alt": alt, "css_class": css_class}
