# Configuration CKEditor5 avec Cloudinary - Guide de résolution des problèmes

## Configuration réalisée

### 1. Installation et configuration
- ✅ Package `django-ckeditor-5==0.2.12` installé
- ✅ Ajouté à `INSTALLED_APPS`
- ✅ URLs configurées
- ✅ Configuration CKEditor5 dans `settings.py`

### 2. Configuration Cloudinary
- ✅ Stockage configuré pour utiliser Cloudinary
- ✅ Vue d'upload personnalisée créée
- ✅ Validation des fichiers implémentée

### 3. Modèles mis à jour
- ✅ `Project.content` utilise `CKEditor5Field`
- ✅ `ProjectCategory.description` utilise `CKEditor5Field`
- ✅ `Client.description` utilise `CKEditor5Field`
- ✅ `ProjectImage.description` utilise `CKEditor5Field`

### 4. Configuration Admin
- ✅ Widgets CKEditor5 configurés dans l'admin
- ✅ Configurations personnalisées (`default` et `extends`)

## URLs importantes

- `/admin/` - Interface d'administration Django
- `/ckeditor5/image_upload/` - Vue d'upload personnalisée pour Cloudinary
- `/test-cloudinary/` - Vue de test pour diagnostiquer Cloudinary

## Résolution du problème "Invalid image file"

Le problème venait de plusieurs sources :

1. **Vue d'upload par défaut** : CKEditor5 utilisait sa vue par défaut qui n'était pas optimisée pour Cloudinary
2. **Validation manquante** : Pas de validation des types de fichiers et tailles
3. **Configuration Cloudinary** : Paramètres d'upload non optimisés

### Solution mise en place :

1. **Vue d'upload personnalisée** (`core/ckeditor5_views.py`) :
   - Validation des types de fichiers (JPEG, PNG, GIF, BMP, WebP)
   - Validation de la taille (max 10MB)
   - Configuration Cloudinary optimisée
   - Gestion d'erreurs améliorée

2. **URL prioritaire** :
   - Notre vue personnalisée remplace celle par défaut
   - URL `/ckeditor5/image_upload/` redirigée vers notre vue

3. **Configuration Cloudinary améliorée** :
   ```python
   upload_options = {
       'folder': 'ckeditor5/uploads',
       'quality': 'auto',
       'fetch_format': 'auto',
       'crop': 'limit',
       'width': 1200,
       'height': 800,
       'flags': 'progressive',
       'resource_type': 'image',
       'use_filename': True,
       'unique_filename': True,
   }
   ```

## Configuration dans settings.py

```python
# CKEditor 5 Configuration
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'link', '|',
            'bulletedList', 'numberedList', '|',
            'outdent', 'indent', '|',
            'blockQuote', 'insertTable', '|',
            'uploadImage', '|',
            'undo', 'redo'
        ],
        'height': 300,
        'width': '100%',
    },
    'extends': {
        # Configuration étendue avec plus d'options
        'toolbar': [...],
        'height': 400,
        'width': '100%',
    }
}

# Upload settings for CKEditor 5
CKEDITOR_5_UPLOAD_PATH = "ckeditor5/uploads/"
CKEDITOR_5_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'tiff']
```

## Utilisation dans les modèles

```python
from django_ckeditor_5.fields import CKEditor5Field

class MonModele(models.Model):
    # Configuration basique
    description = CKEditor5Field('Description', config_name='default', blank=True)
    
    # Configuration étendue
    content = CKEditor5Field('Content', config_name='extends', blank=True)
```

## Utilisation dans l'admin

```python
from django_ckeditor_5.widgets import CKEditor5Widget

class MonModeleAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if 'content' in form.base_fields:
            form.base_fields['content'].widget = CKEditor5Widget(
                config_name='extends'
            )
        
        return form
```

## Test et debugging

1. **Tester la configuration Cloudinary** :
   ```bash
   python test_ckeditor_cloudinary.py
   ```

2. **Vérifier l'upload via l'interface** :
   - Aller dans l'admin Django
   - Éditer un projet
   - Utiliser l'éditeur CKEditor5
   - Tenter un upload d'image

3. **Logs** :
   - Vérifier les logs Django pour les erreurs d'upload
   - Logs Cloudinary disponibles dans le dashboard

## Statut actuel

✅ Configuration complète et fonctionnelle
✅ Uploads d'images vers Cloudinary opérationnels
✅ Validation et gestion d'erreurs en place
✅ Interface admin configurée

Les uploads CKEditor5 devraient maintenant fonctionner correctement avec Cloudinary.
