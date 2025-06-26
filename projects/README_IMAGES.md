# Système de Gestion des Images avec Cloudinary

Ce système génère automatiquement des versions optimisées de toutes les images uploadées dans les modèles Django en utilisant Cloudinary.

## 🚀 Fonctionnalités

### Génération automatique des versions d'images
- **Projets** (`Project`): `featured_image` → `featured_image_large` (1200x800) + `thumbnail` (400x300)
- **Images de galerie** (`ProjectImage`): `image` → `image_large` (1200x800) + `image_thumbnail` (300x200)
- **Clients** (`Client`): 
  - `logo` → `logo_large` (400px max) + `logo_thumbnail` (150x150)
  - `logo_white` → `logo_white_large` (400px max) + `logo_white_thumbnail` (150x150)
- **Témoignages** (`ProjectTestimonial`): `client_photo` → `client_photo_large` (200x200) + `client_photo_thumbnail` (80x80)

### Nettoyage automatique
- Suppression automatique des images Cloudinary lors de la suppression des objets Django
- Commande pour nettoyer les images orphelines

## 📁 Structure des dossiers Cloudinary

```
projects/
├── featured/
│   ├── original/     # Images originales des projets
│   ├── large/        # Versions 1200x800 pour affichage principal
│   └── thumbnails/   # Versions 400x300 pour listes/grilles
├── gallery/
│   ├── original/     # Images originales de galerie
│   ├── large/        # Versions 1200x800 pour affichage principal
│   └── thumbnails/   # Versions 300x200 pour miniatures
clients/
├── logos/
│   ├── original/     # Logos originaux
│   ├── large/        # Versions 400px max
│   └── thumbnails/   # Versions 150x150
│   └── white/
│       ├── original/ # Logos blancs originaux
│       ├── large/    # Versions 400px max
│       └── thumbnails/ # Versions 150x150
testimonials/
├── original/         # Photos clients originales
├── large/           # Versions 200x200 (avec focus visage)
└── thumbnails/      # Versions 80x80 (avec focus visage)
```

## 🔧 Commandes de gestion

### Générer les versions d'images pour les contenus existants

```bash
# Générer toutes les versions manquantes
python manage.py generate_image_versions

# Générer seulement pour les projets
python manage.py generate_image_versions --model project

# Générer seulement pour les clients
python manage.py generate_image_versions --model client

# Générer seulement pour les témoignages
python manage.py generate_image_versions --model testimonial

# Générer seulement pour les images de galerie
python manage.py generate_image_versions --model projectimage

# Forcer la régénération même si les versions existent déjà
python manage.py generate_image_versions --force
```

### Nettoyer les images orphelines sur Cloudinary

```bash
# Voir quelles images seraient supprimées (sans supprimer)
python manage.py cleanup_orphaned_images --dry-run

# Nettoyer toutes les images orphelines
python manage.py cleanup_orphaned_images

# Nettoyer un dossier spécifique
python manage.py cleanup_orphaned_images --folder projects/featured
```

## ⚡ Utilisation automatique

### Lors de la création/modification d'objets

Les signaux Django se déclenchent automatiquement :

```python
# Exemple : Créer un projet
project = Project.objects.create(
    title="Mon Projet",
    featured_image=mon_image,  # Upload de l'image originale
    # ... autres champs
)

# Les versions optimisées sont générées automatiquement en arrière-plan
# project.featured_image_large et project.thumbnail seront disponibles
```

### Accès aux URL des images

```python
# Dans les templates ou le code Python
project = Project.objects.get(id=1)

# URLs via les propriétés
urls = project.featured_image_urls
# {
#   'original': 'https://res.cloudinary.com/...',
#   'large': 'https://res.cloudinary.com/...',
#   'thumbnail': 'https://res.cloudinary.com/...'
# }

# URLs directes (compatibilité)
original_url = project.featured_image.url
large_url = project.featured_image_url  # Retourne large ou original
thumb_url = project.thumbnail_url       # Retourne thumbnail ou original
```

### Dans les templates Django

```html
<!-- Image principale du projet -->
<img src="{{ project.featured_image_url }}" alt="{{ project.title }}">

<!-- Miniature pour une liste -->
<img src="{{ project.thumbnail_url }}" alt="{{ project.title }}">

<!-- Toutes les versions disponibles -->
{% with urls=project.featured_image_urls %}
    <picture>
        <source media="(min-width: 768px)" srcset="{{ urls.large }}">
        <source media="(max-width: 767px)" srcset="{{ urls.thumbnail }}">
        <img src="{{ urls.original }}" alt="{{ project.title }}">
    </picture>
{% endwith %}

<!-- Logo client avec fallback -->
{% with urls=project.client.logo_urls %}
    <img src="{{ urls.thumbnail|default:urls.original }}" alt="{{ project.client.name }}">
{% endwith %}
```

## 🔒 Gestion des erreurs

Le système inclut une gestion robuste des erreurs :
- Logging des erreurs de génération/suppression
- Transactions atomiques pour éviter les états incohérents
- Fallback vers l'image originale si les versions optimisées échouent

## 📊 Monitoring

Surveillez les logs Django pour les messages liés aux images :

```python
# Dans settings.py, configurez le logging
LOGGING = {
    'loggers': {
        'projects.signals': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚨 Maintenance

### Migration des images existantes

Après l'installation de ce système sur un projet existant :

```bash
# 1. Générer toutes les versions manquantes
python manage.py generate_image_versions

# 2. Vérifier qu'il n'y a pas d'orphelins
python manage.py cleanup_orphaned_images --dry-run

# 3. Nettoyer les orphelins si nécessaire
python manage.py cleanup_orphaned_images
```

### Sauvegarde avant nettoyage

Avant de faire un nettoyage important :

```bash
# Backup des métadonnées Cloudinary
python manage.py dumpdata projects.Project projects.Client projects.ProjectImage projects.ProjectTestimonial > backup_images_metadata.json
```
