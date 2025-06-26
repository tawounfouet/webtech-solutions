#!/usr/bin/env python
"""
Script de test pour vérifier la configuration CKEditor5 + Cloudinary
"""
import os
import sys
import django

# Ajouter le chemin du projet
sys.path.append('/workspaces/webtech-solutions')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from django.conf import settings
import cloudinary
import cloudinary.uploader

def test_cloudinary_config():
    """Test de la configuration Cloudinary"""
    print("=== Test de configuration Cloudinary ===")
    
    # Vérifier les variables d'environnement
    print(f"CLOUDINARY_CLOUD_NAME: {os.getenv('CLOUDINARY_CLOUD_NAME', 'Non défini')}")
    print(f"CLOUDINARY_API_KEY: {os.getenv('CLOUDINARY_API_KEY', 'Non défini')}")
    print(f"CLOUDINARY_API_SECRET: {'*' * 10 if os.getenv('CLOUDINARY_API_SECRET') else 'Non défini'}")
    
    # Vérifier la configuration Django
    print(f"CKEDITOR_5_FILE_STORAGE: {getattr(settings, 'CKEDITOR_5_FILE_STORAGE', 'Non défini')}")
    print(f"CKEDITOR_5_UPLOAD_PATH: {getattr(settings, 'CKEDITOR_5_UPLOAD_PATH', 'Non défini')}")
    
    # Test de connexion Cloudinary
    try:
        result = cloudinary.api.ping()
        print(f"✅ Connexion Cloudinary: OK - {result}")
    except Exception as e:
        print(f"❌ Erreur Cloudinary: {e}")

def test_ckeditor_config():
    """Test de la configuration CKEditor5"""
    print("\n=== Test de configuration CKEditor5 ===")
    
    ckeditor_configs = getattr(settings, 'CKEDITOR_5_CONFIGS', {})
    print(f"Configurations disponibles: {list(ckeditor_configs.keys())}")
    
    for config_name, config in ckeditor_configs.items():
        print(f"\nConfiguration '{config_name}':")
        print(f"  - Toolbar: {len(config.get('toolbar', []))} éléments")
        print(f"  - Hauteur: {config.get('height', 'Non défini')}")
        print(f"  - Image config: {'Oui' if 'image' in config else 'Non'}")

if __name__ == '__main__':
    test_cloudinary_config()
    test_ckeditor_config()
    print("\n=== Test terminé ===")
