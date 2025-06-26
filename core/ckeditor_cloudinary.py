"""
Configuration personnalisée pour CKEditor5 avec Cloudinary
"""
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import cloudinary
import cloudinary.uploader
import cloudinary.exceptions

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
def ckeditor_upload_file(request):
    """
    Vue personnalisée pour l'upload de fichiers CKEditor5 vers Cloudinary
    avec optimisations automatiques et validation améliorée
    """
    if request.method == 'POST' and 'upload' in request.FILES:
        upload_file = request.FILES['upload']
        
        # Validation du fichier
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
        max_size = 10 * 1024 * 1024  # 10MB
        
        # Vérifier le type de fichier
        if upload_file.content_type not in allowed_types:
            return JsonResponse({
                'uploaded': False,
                'error': {
                    'message': f'Type de fichier non supporté. Types autorisés: {", ".join(allowed_types)}'
                }
            })
        
        # Vérifier la taille du fichier
        if upload_file.size > max_size:
            return JsonResponse({
                'uploaded': False,
                'error': {
                    'message': f'Fichier trop volumineux. Taille maximale: {max_size // (1024*1024)}MB'
                }
            })
        
        try:
            # Configuration pour l'upload vers Cloudinary
            upload_options = {
                'folder': 'ckeditor5/uploads',
                'quality': 'auto',
                'fetch_format': 'auto',
                'crop': 'limit',
                'width': 1200,  # Limite la largeur max
                'height': 800,  # Limite la hauteur max
                'flags': 'progressive',  # Pour un chargement progressif
                'resource_type': 'image',  # Spécifier explicitement le type de ressource
                'use_filename': True,
                'unique_filename': True,
            }
            
            # Lire le contenu du fichier
            upload_file.seek(0)  # S'assurer qu'on lit depuis le début
            
            # Upload vers Cloudinary
            result = cloudinary.uploader.upload(
                upload_file,
                **upload_options
            )
            
            logger.info(f"Upload CKEditor5 réussi: {result.get('public_id', 'unknown')}")
            
            # Retourner la réponse au format attendu par CKEditor5
            return JsonResponse({
                'url': result['secure_url'],
                'uploaded': True,
            })
            
        except cloudinary.exceptions.Error as e:
            logger.error(f"Erreur Cloudinary lors de l'upload CKEditor5: {str(e)}")
            return JsonResponse({
                'uploaded': False,
                'error': {
                    'message': f'Erreur Cloudinary: {str(e)}'
                }
            })
        except Exception as e:
            logger.error(f"Erreur générale lors de l'upload CKEditor5 vers Cloudinary: {str(e)}")
            return JsonResponse({
                'uploaded': False,
                'error': {
                    'message': f'Erreur lors de l\'upload: {str(e)}'
                }
            })
    
    return JsonResponse({
        'uploaded': False,
        'error': {
            'message': 'Aucun fichier fourni ou méthode incorrecte'
        }
    })


def get_ckeditor_cloudinary_config():
    """
    Retourne la configuration CKEditor5 optimisée pour Cloudinary
    """
    return {
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
            'image': {
                'toolbar': [
                    'imageTextAlternative', '|',
                    'imageStyle:alignLeft',
                    'imageStyle:alignRight',
                    'imageStyle:alignCenter',
                    'imageStyle:side', '|'
                ],
                'styles': [
                    'full',
                    'side',
                    'alignLeft',
                    'alignRight',
                    'alignCenter',
                ]
            },
        },
        'extends': {
            'blockToolbar': [
                'paragraph', 'heading1', 'heading2', 'heading3',
                '|',
                'bulletedList', 'numberedList',
                '|',
                'blockQuote', 'uploadImage'
            ],
            'toolbar': [
                'heading', '|',
                'outdent', 'indent', '|',
                'bold', 'italic', 'link', 'underline', 'strikethrough',
                'code', 'subscript', 'superscript', 'highlight', '|',
                'codeBlock', 'sourceEditing', 'uploadImage',
                'bulletedList', 'numberedList', 'todoList', '|',
                'blockQuote', 'insertTable', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor',
                'mediaEmbed', 'removeFormat', '|',
                'undo', 'redo'
            ],
            'image': {
                'toolbar': [
                    'imageTextAlternative', '|',
                    'imageStyle:alignLeft',
                    'imageStyle:alignRight',
                    'imageStyle:alignCenter',
                    'imageStyle:side', '|'
                ],
                'styles': [
                    'full',
                    'side',
                    'alignLeft',
                    'alignRight',
                    'alignCenter',
                ]
            },
            'table': {
                'contentToolbar': [
                    'tableColumn',
                    'tableRow',
                    'mergeTableCells'
                ],
                'tableToolbar': ['comment', 'tableColumn', 'tableRow', 'mergeTableCells']
            },
            'height': 400,
            'width': '100%',
        },
        'list': {
            'properties': {
                'styles': 'true',
                'startIndex': 'true',
                'reversed': 'true',
            }
        }
    }


@login_required
def test_cloudinary_config(request):
    """
    Vue de test pour vérifier la configuration Cloudinary
    """
    try:
        # Test de connexion
        ping_result = cloudinary.api.ping()
        
        # Test d'upload d'une image simple
        test_result = cloudinary.uploader.upload(
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            folder='test',
            public_id='test_image'
        )
        
        return JsonResponse({
            'status': 'success',
            'ping': ping_result,
            'upload_test': test_result.get('secure_url', 'No URL'),
            'message': 'Configuration Cloudinary fonctionnelle'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'message': 'Problème avec la configuration Cloudinary'
        })
