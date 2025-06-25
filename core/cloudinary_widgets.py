"""
Widgets personnalisés pour l'administration Django avec Cloudinary
"""

from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
import cloudinary
from cloudinary import CloudinaryImage


class CloudinaryImageWidget(forms.ClearableFileInput):
    """Widget personnalisé pour afficher les images Cloudinary dans l'admin"""

    template_name = "admin/cloudinary_image_widget.html"

    def __init__(self, attrs=None):
        default_attrs = {"accept": "image/*"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        """Formate la valeur pour l'affichage"""
        if value and hasattr(value, "url"):
            return value.url
        return value

    def render(self, name, value, attrs=None, renderer=None):
        """Rendu personnalisé du widget"""
        html = super().render(name, value, attrs, renderer)

        if value and hasattr(value, "url"):
            # Générer une miniature Cloudinary
            try:
                thumbnail_url = CloudinaryImage(str(value)).build_url(
                    width=150, height=150, crop="fill", fetch_format="auto", quality="auto"
                )

                preview_html = f"""
                <div class="cloudinary-preview" style="margin-top: 10px;">
                    <img src="{thumbnail_url}" 
                         alt="Aperçu" 
                         style="max-width: 150px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px;">
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">
                        <strong>URL Cloudinary:</strong> {value}
                    </p>
                </div>
                """
                html += preview_html
            except Exception:
                pass

        return mark_safe(html)


class CloudinaryImageField(forms.ImageField):
    """Champ personnalisé pour les images Cloudinary"""

    widget = CloudinaryImageWidget

    def __init__(self, *args, **kwargs):
        self.cloudinary_folder = kwargs.pop("cloudinary_folder", None)
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance=None):
        """Validation personnalisée"""
        cleaned = super().clean(value, model_instance)
        return cleaned
