"""
Vue d'upload personnalisée pour CKEditor5 avec Cloudinary
Compatible avec django-ckeditor-5
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import cloudinary
import cloudinary.uploader
import cloudinary.exceptions

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """
    Vue d'upload pour CKEditor5 qui remplace la vue par défaut
    Compatible avec l'API de django-ckeditor-5
    """
    if 'upload' not in request.FILES:
        return JsonResponse({
            'uploaded': False,
            'error': {
                'message': 'Aucun fichier fourni'
            }
        })
    
    upload_file = request.FILES['upload']
    
    # Validation du fichier
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
    max_size = 10 * 1024 * 1024  # 10MB
    
    # Vérifier le type de fichier
    if upload_file.content_type not in allowed_types:
        return JsonResponse({
            'uploaded': False,
            'error': {
                'message': f'Type de fichier non supporté: {upload_file.content_type}. Types autorisés: JPEG, PNG, GIF, BMP, WebP'
            }
        })
    
    # Vérifier la taille du fichier
    if upload_file.size > max_size:
        return JsonResponse({
            'uploaded': False,
            'error': {
                'message': f'Fichier trop volumineux ({upload_file.size} bytes). Taille maximale: {max_size // (1024*1024)}MB'
            }
        })
    
    try:
        # Configuration pour l'upload vers Cloudinary
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
        
        # S'assurer qu'on lit depuis le début du fichier
        upload_file.seek(0)
        
        # Upload vers Cloudinary
        result = cloudinary.uploader.upload(
            upload_file,
            **upload_options
        )
        
        logger.info(f"Upload CKEditor5 réussi: {result.get('public_id', 'unknown')} - URL: {result.get('secure_url', 'unknown')}")
        
        # Retourner la réponse au format attendu par CKEditor5
        return JsonResponse({
            'url': result['secure_url'],
            'uploaded': True,
        })
        
    except cloudinary.exceptions.Error as e:
        error_msg = f"Erreur Cloudinary: {str(e)}"
        logger.error(f"Erreur Cloudinary lors de l'upload CKEditor5: {error_msg}")
        return JsonResponse({
            'uploaded': False,
            'error': {
                'message': error_msg
            }
        })
    except Exception as e:
        error_msg = f"Erreur lors de l'upload: {str(e)}"
        logger.error(f"Erreur générale lors de l'upload CKEditor5: {error_msg}")
        return JsonResponse({
            'uploaded': False,
            'error': {
                'message': error_msg
            }
        })
