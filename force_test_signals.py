#!/usr/bin/env python
"""
Script pour forcer un test des signaux en réinitialisant les versions d'images
"""
import os
import sys
import django

# Configurer Django
sys.path.append('/workspaces/webtech-solutions')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from projects.models import Project
import logging

# Configurer le logging pour voir les messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

def force_test_signals():
    print("🧪 Test forcé des signaux Django...")
    
    # Récupérer un projet avec une image
    project = Project.objects.filter(featured_image__isnull=False).first()
    
    if not project:
        print("❌ Aucun projet avec une image principale trouvé.")
        return
    
    print(f"📝 Projet testé: {project.title}")
    print(f"   Image principale: {project.featured_image.url if project.featured_image else 'None'}")
    
    # Sauvegarder les valeurs actuelles
    original_large = project.featured_image_large
    original_thumb = project.thumbnail
    original_public_id = project.featured_image_cloudinary_public_id
    
    print("🔄 Suppression temporaire des versions...")
    # Supprimer temporairement les versions pour forcer la régénération
    project.featured_image_large = None
    project.thumbnail = None
    project.featured_image_cloudinary_public_id = ""
    
    # Sauvegarder sans déclencher les signaux
    Project.objects.filter(pk=project.pk).update(
        featured_image_large=None,
        thumbnail=None,
        featured_image_cloudinary_public_id=""
    )
    
    # Recharger l'instance
    project.refresh_from_db()
    
    print("📊 État avant déclenchement du signal:")
    print(f"   featured_image: {bool(project.featured_image)}")
    print(f"   featured_image_large: {bool(project.featured_image_large)}")
    print(f"   thumbnail: {bool(project.thumbnail)}")
    
    print("🚀 Déclenchement du signal via save()...")
    # Déclencher le signal
    project.save()
    
    # Recharger depuis la base
    project.refresh_from_db()
    
    print("📊 État après déclenchement du signal:")
    print(f"   featured_image_large: {bool(project.featured_image_large)}")
    print(f"   thumbnail: {bool(project.thumbnail)}")
    print(f"   featured_image_cloudinary_public_id: {bool(project.featured_image_cloudinary_public_id)}")
    
    if project.featured_image_large and project.thumbnail:
        print("✅ Signaux fonctionnent correctement!")
        if project.featured_image_large:
            print(f"   URL large: {project.featured_image_large}")
        if project.thumbnail:
            print(f"   URL thumbnail: {project.thumbnail}")
    else:
        print("❌ Les signaux ne fonctionnent pas comme attendu.")
        print("🔄 Restauration des valeurs originales...")
        # Restaurer les valeurs originales
        Project.objects.filter(pk=project.pk).update(
            featured_image_large=original_large,
            thumbnail=original_thumb,
            featured_image_cloudinary_public_id=original_public_id
        )

if __name__ == "__main__":
    force_test_signals()
