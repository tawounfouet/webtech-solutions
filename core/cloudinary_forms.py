from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from cloudinary.forms import CloudinaryFileField
from cloudinary import CloudinaryImage


class CloudinaryImageWidget(forms.ClearableFileInput):
    """Widget personnalisé pour les champs CloudinaryField avec aperçu"""

    def __init__(self, attrs=None):
        default_attrs = {"class": "cloudinary-widget"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        """Formate la valeur pour l'affichage"""
        if value and hasattr(value, "url"):
            return value.url
        elif value:
            return str(value)
        return None

    def _get_image_url(self, value):
        """Extrait l'URL de l'image"""
        if hasattr(value, "url"):
            return value.url
        return str(value)

    def _create_preview_html(self, image_url):
        """Génère le HTML d'aperçu de l'image"""
        try:
            # Extract public_id for CloudinaryImage
            public_id = self._extract_public_id(image_url)
            
            thumbnail_url = CloudinaryImage(public_id).build_url(
                width=200, height=150, crop="fill", fetch_format="auto", quality="auto"
            )

            return format_html(
                """
                <div class="cloudinary-preview" style="margin: 10px 0; padding: 10px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px;">
                    <img src="{}" style="max-width: 200px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />
                    <p style="margin: 5px 0; font-size: 11px; color: #666;">
                        <strong>Image actuelle (hébergée sur Cloudinary)</strong>
                    </p>
                </div>
                """,
                thumbnail_url,
            )
        except Exception as e:
            return format_html(
                '<p style="color: #d63031; font-size: 11px;">⚠️ Erreur lors du chargement de l\'aperçu: {}</p>',
                str(e)
            )

    def _extract_public_id(self, image_url):
        """Extrait le public_id depuis une URL Cloudinary"""
        if "/" not in image_url or "cloudinary.com" not in image_url:
            return image_url
        
        try:
            parts = image_url.split("/")
            upload_idx = parts.index("upload")
            public_id = "/".join(parts[upload_idx + 2:])
            
            # Remove file extension
            if "." in public_id:
                public_id = public_id.rsplit(".", 1)[0]
            
            # Remove version prefix if present
            if public_id.startswith("v") and len(public_id.split("/")) > 1:
                parts = public_id.split("/")
                if parts[0][1:].isdigit():
                    public_id = "/".join(parts[1:])
            
            return public_id
        except (ValueError, IndexError):
            return image_url

    def _create_help_html(self):
        """Génère le HTML d'aide"""
        return format_html(
            """
            <div class="cloudinary-help" style="margin: 10px 0; padding: 10px; background: #e8f4f8; border-left: 4px solid #17a2b8; font-size: 11px;">
                <strong>💡 Conseils pour l'upload Cloudinary :</strong>
                <ul style="margin: 5px 0 0 20px; padding: 0;">
                    <li>Formats supportés : JPG, PNG, WebP, GIF</li>
                    <li>Taille recommandée : minimum 800px de largeur</li>
                    <li>L'image sera automatiquement optimisée par Cloudinary</li>
                    <li>Redimensionnement et compression automatiques</li>
                </ul>
            </div>
            """
        )

    def render(self, name, value, attrs=None, renderer=None):
        """Rendu du widget avec aperçu de l'image"""
        widget_html = super().render(name, value, attrs, renderer)
        
        preview_html = ""
        if value:
            image_url = self._get_image_url(value)
            preview_html = self._create_preview_html(image_url)
        
        help_html = self._create_help_html()
        
        return mark_safe(preview_html + widget_html + help_html)


class CloudinaryImageField(CloudinaryFileField):
    """Champ personnalisé avec widget amélioré"""

    widget = CloudinaryImageWidget

    def __init__(self, *args, **kwargs):
        # Options par défaut pour Cloudinary
        default_options = {
            "folder": "uploads",
            "use_filename": True,
            "unique_filename": False,
            "overwrite": False,
            "resource_type": "image",
            "fetch_format": "auto",
            "quality": "auto",
        }

        # Merge avec les options fournies
        options = kwargs.pop("options", {})
        default_options.update(options)
        kwargs["options"] = default_options

        super().__init__(*args, **kwargs)
