#!/usr/bin/env python
"""
Script de test pour vérifier que les signaux fonctionnent correctement
"""
import os
import sys
import django

# Configurer Django
sys.path.append('/workspaces/webtech-solutions')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from projects.models import Project, Client
import logging

# Configurer le logging pour voir les messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('projects.signals')

def test_signals():
    print("🧪 Test des signaux Django...")
    
    # Récupérer ou créer un client de test
    client, created = Client.objects.get_or_create(
        name="Test Client",
        defaults={'slug': 'test-client'}
    )
    
    # Récupérer un projet existant ou en créer un
    project = Project.objects.filter(featured_image__isnull=False).first()
    
    if not project:
        print("❌ Aucun projet avec une image principale trouvé.")
        print("   Créez d'abord un projet avec une image via l'admin Django.")
        return
    
    print(f"📝 Projet testé: {project.title}")
    print(f"   Image principale: {bool(project.featured_image)}")
    print(f"   Version large: {bool(project.featured_image_large)}")
    print(f"   Thumbnail: {bool(project.thumbnail)}")
    
    if project.featured_image and not project.featured_image_large:
        print("🔄 Déclenchement manuel du signal...")
        # Simuler une sauvegarde pour déclencher le signal
        project.save()
        
        # Recharger depuis la base
        project.refresh_from_db()
        
        print(f"   Version large après signal: {bool(project.featured_image_large)}")
        print(f"   Thumbnail après signal: {bool(project.thumbnail)}")
        
        if project.featured_image_large and project.thumbnail:
            print("✅ Signaux fonctionnent correctement!")
        else:
            print("❌ Les signaux ne semblent pas fonctionner.")
    else:
        print("ℹ️  Les versions existent déjà ou pas d'image principale.")

if __name__ == "__main__":
    test_signals()
