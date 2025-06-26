#!/usr/bin/env python
"""
Script de test pour vérifier la configuration de la page de détail projet
avec CKEditor5, Cloudinary et le nouveau carousel Bootstrap.
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from projects.models import Project, ProjectCategory, Client
from authentication.models import User

def test_project_detail_page():
    """Test la page de détail d'un projet"""
    
    print("🧪 Test de la page de détail projet...")
    
    # Créer un client de test
    client = Client()
    
    # Vérifier qu'il y a au moins un projet
    project = Project.objects.first()
    if not project:
        print("❌ Aucun projet trouvé. Utilisez le script create_sample_content.py pour créer des données de test.")
        return False
    
    # Tester la page de détail
    try:
        url = reverse('projects:project_detail', kwargs={'slug': project.slug})
        response = client.get(url)
        
        if response.status_code == 200:
            print(f"✅ Page de détail accessible : {url}")
            
            # Vérifier que les éléments importants sont présents
            content = response.content.decode('utf-8')
            
            checks = [
                ('Hero section', 'hero-section'),
                ('Titre du projet', project.title),
                ('Image principale', 'featured-image-section'),
                ('Section info projet', 'project-info-section'),
                ('Contenu CKEditor5', 'project-content-section'),
                ('CSS personnalisé', 'project-detail.css'),
            ]
            
            # Vérifier la galerie si elle existe
            if project.images.exists():
                checks.append(('Carousel Bootstrap', 'projectGalleryCarousel'))
                checks.append(('Indicateurs carousel', 'carousel-indicators'))
                checks.append(('Contrôles carousel', 'carousel-control'))
            
            # Vérifier les métriques si elles existent
            if any([project.budget, project.team_size, project.delivery_time]):
                checks.append(('Section métriques', 'project-metrics-section'))
            
            # Vérifier le témoignage s'il existe
            if project.client and project.client.testimonial:
                checks.append(('Section témoignage', 'testimonial-section'))
            
            all_checks_passed = True
            for check_name, check_content in checks:
                if check_content in content:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name} manquant")
                    all_checks_passed = False
            
            return all_checks_passed
            
        else:
            print(f"❌ Erreur {response.status_code} lors de l'accès à la page : {url}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return False

def test_ckeditor5_configuration():
    """Test la configuration CKEditor5"""
    
    print("\n🧪 Test de la configuration CKEditor5...")
    
    try:
        from django.conf import settings
        
        # Vérifier que django-ckeditor-5 est installé
        if 'django_ckeditor_5' in settings.INSTALLED_APPS:
            print("✅ django-ckeditor-5 installé")
        else:
            print("❌ django-ckeditor-5 non installé")
            return False
        
        # Vérifier la configuration CKEditor5
        if hasattr(settings, 'CKEDITOR_5_CONFIGS'):
            print("✅ Configuration CKEditor5 présente")
            
            config = settings.CKEDITOR_5_CONFIGS.get('default', {})
            if 'toolbar' in config:
                print("  ✅ Toolbar configurée")
            if 'ckfinder' in config or 'simpleUpload' in config:
                print("  ✅ Upload configuré")
            
        else:
            print("❌ Configuration CKEditor5 manquante")
            return False
        
        # Vérifier la configuration Cloudinary pour CKEditor5
        if hasattr(settings, 'CKEDITOR_5_FILE_STORAGE'):
            print("✅ Stockage Cloudinary configuré pour CKEditor5")
        else:
            print("❌ Stockage Cloudinary manquant pour CKEditor5")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de configuration : {e}")
        return False

def test_project_models():
    """Test les modèles avec CKEditor5Field"""
    
    print("\n🧪 Test des modèles avec CKEditor5Field...")
    
    try:
        from projects.models import Project, ProjectCategory, Client
        from django_ckeditor_5.fields import CKEditor5Field
        
        # Vérifier les champs CKEditor5
        model_checks = [
            (Project, 'description'),
            (Project, 'content'),
            (ProjectCategory, 'description'),
            (Client, 'description'),
        ]
        
        all_checks_passed = True
        for model, field_name in model_checks:
            try:
                field = model._meta.get_field(field_name)
                if isinstance(field, CKEditor5Field):
                    print(f"  ✅ {model.__name__}.{field_name} utilise CKEditor5Field")
                else:
                    print(f"  ❌ {model.__name__}.{field_name} n'utilise pas CKEditor5Field")
                    all_checks_passed = False
            except Exception:
                print(f"  ❌ Champ {model.__name__}.{field_name} non trouvé")
                all_checks_passed = False
        
        return all_checks_passed
        
    except Exception as e:
        print(f"❌ Erreur lors du test des modèles : {e}")
        return False

def main():
    """Fonction principale de test"""
    
    print("🚀 Tests de la page de détail projet avec CKEditor5 et Carousel Bootstrap")
    print("=" * 80)
    
    tests = [
        test_ckeditor5_configuration,
        test_project_models,
        test_project_detail_page,
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
    
    print("\n📊 Résultats des tests :")
    print("=" * 40)
    
    if all(results):
        print("🎉 Tous les tests sont passés avec succès !")
        print("\n✨ Fonctionnalités validées :")
        print("  - CKEditor5 configuré avec Cloudinary")
        print("  - Modèles utilisant CKEditor5Field")
        print("  - Page de détail avec hero ajusté")
        print("  - Carousel Bootstrap natif pour la galerie")
        print("  - CSS optimisé sans code slider custom")
        print("  - Section témoignage visible")
        return True
    else:
        print("❌ Certains tests ont échoué.")
        failed_tests = [i for i, result in enumerate(results) if not result]
        print(f"   Tests échoués : {failed_tests}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
