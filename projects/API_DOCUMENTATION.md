# API Documentation - Projets WebTech Solutions

## Vue d'ensemble

Les APIs fournissent un accès programmatique aux données des projets, clients, et catégories avec un système d'images multi-formats optimisé.

## Endpoints disponibles

### 📊 **Statistiques des projets**
```
GET /projects/api/stats/
```
Retourne des statistiques complètes sur les projets, clients et catégories.

**Réponse :**
```json
{
  "stats": {
    "total_projects": 25,
    "published_projects": 20,
    "featured_projects": 6,
    "draft_projects": 3,
    "completed_projects": 18,
    "active_clients": 12,
    "total_categories": 5,
    "by_status": {
      "completed": 18,
      "in_progress": 4,
      "draft": 3
    },
    "by_category": [
      {
        "name": "Développement Web",
        "color": "#007cba",
        "project_count": 8
      }
    ],
    "top_clients": [
      {
        "name": "Entreprise ABC",
        "slug": "entreprise-abc",
        "project_count": 5,
        "logo_url": "https://res.cloudinary.com/..."
      }
    ],
    "recent_projects": [
      {
        "title": "Site E-commerce",
        "slug": "site-ecommerce",
        "client": "Entreprise ABC",
        "status": "completed",
        "created_at": "2025-01-15T10:30:00Z",
        "thumbnail_url": "https://res.cloudinary.com/..."
      }
    ]
  }
}
```

### 🏢 **Liste des clients**
```
GET /projects/api/clients/
```
Retourne tous les clients actifs avec leurs logos multi-formats.

**Réponse :**
```json
{
  "clients": [
    {
      "id": 1,
      "name": "Entreprise ABC",
      "slug": "entreprise-abc",
      "website": "https://entreprise-abc.com",
      "description": "Description du client",
      "logo_urls": {
        "original": "https://res.cloudinary.com/.../original",
        "large": "https://res.cloudinary.com/.../large",
        "thumbnail": "https://res.cloudinary.com/.../thumbnail"
      },
      "logo_white_urls": {
        "original": "https://res.cloudinary.com/.../white/original",
        "large": "https://res.cloudinary.com/.../white/large",
        "thumbnail": "https://res.cloudinary.com/.../white/thumbnail"
      },
      "projects_count": 5
    }
  ]
}
```

### 🏷️ **Catégories de projets**
```
GET /projects/api/categories/
```
Retourne toutes les catégories avec leurs couleurs et compteurs de projets.

**Réponse :**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Développement Web",
      "slug": "developpement-web",
      "description": "Création de sites et applications web",
      "color": "#007cba",
      "projects_count": 8
    }
  ]
}
```

### 🎨 **Portfolio complet**
```
GET /projects/api/portfolio/
```
Retourne une liste complète des projets avec filtres optionnels.

**Paramètres de requête :**
- `category` : Slug de la catégorie
- `client` : Slug du client  
- `featured` : `true` pour les projets mis en avant uniquement
- `limit` : Nombre maximum de projets (défaut: 20)

**Exemple :**
```
GET /projects/api/portfolio/?category=developpement-web&featured=true&limit=10
```

**Réponse :**
```json
{
  "projects": [
    {
      "id": 1,
      "title": "Site E-commerce",
      "slug": "site-ecommerce",
      "subtitle": "Plateforme de vente en ligne moderne",
      "description": "Description courte du projet",
      "client": {
        "name": "Entreprise ABC",
        "slug": "entreprise-abc",
        "logo_urls": {
          "original": "...",
          "large": "...",
          "thumbnail": "..."
        }
      },
      "categories": [
        {
          "name": "Développement Web",
          "slug": "developpement-web",
          "color": "#007cba"
        }
      ],
      "image_urls": {
        "original": "https://res.cloudinary.com/.../original",
        "large": "https://res.cloudinary.com/.../large", 
        "thumbnail": "https://res.cloudinary.com/.../thumbnail"
      },
      "is_featured": true,
      "status": "completed",
      "duration_days": 45,
      "created_at": "2025-01-15T10:30:00Z",
      "metrics": {
        "page_views_increase": 150.5,
        "conversion_rate_increase": 25.3,
        "seo_score": 95,
        "performance_score": 88
      },
      "testimonial": {
        "client_name": "Jean Dupont",
        "client_position": "Directeur Marketing",
        "quote": "Excellent travail, très satisfait du résultat.",
        "rating": 5,
        "client_photo_urls": {
          "original": "...",
          "large": "...",
          "thumbnail": "..."
        }
      }
    }
  ],
  "total_count": 15,
  "filters_applied": {
    "category": "developpement-web",
    "client": null,
    "featured_only": true,
    "limit": 10
  }
}
```

### 🖼️ **Images d'un projet**
```
GET /projects/api/{project_slug}/images/
```
Retourne toutes les images d'un projet spécifique.

**Réponse :**
```json
{
  "project": "Site E-commerce",
  "images": [
    {
      "type": "featured",
      "title": "Site E-commerce",
      "urls": {
        "original": "https://res.cloudinary.com/.../original",
        "large": "https://res.cloudinary.com/.../large",
        "thumbnail": "https://res.cloudinary.com/.../thumbnail"
      }
    },
    {
      "type": "gallery",
      "title": "Page d'accueil",
      "description": "Design de la page d'accueil",
      "urls": {
        "original": "...",
        "large": "...",
        "thumbnail": "..."
      }
    }
  ]
}
```

## 🔧 **Système d'images multi-formats**

Toutes les images sont automatiquement disponibles en 3 versions :

### **Original**
- Image source en qualité maximale
- Pas de transformation appliquée
- Pour téléchargement ou affichage haute qualité

### **Large** 
- Optimisée pour affichage principal
- Dimensions : 1200px max (projets), 400px max (logos)
- Compression automatique (`quality: auto`)
- Format optimal (`fetch_format: auto`)

### **Thumbnail**
- Miniatures pour listes et aperçus
- Dimensions : 300-400px (projets), 80-150px (logos/photos)
- Crop intelligent avec détection de visage (photos clients)

## 📱 **Utilisation frontend**

### **Images responsives**
```html
<img src="{{ project.image_urls.thumbnail }}" 
     srcset="{{ project.image_urls.thumbnail }} 400w,
             {{ project.image_urls.large }} 1200w"
     sizes="(max-width: 768px) 400px, 1200px"
     alt="{{ project.title }}" />
```

### **Logos adaptatifs**
```html
<!-- Logo normal -->
<img src="{{ client.logo_urls.large }}" alt="{{ client.name }}" />

<!-- Logo blanc sur fond sombre -->
<img src="{{ client.logo_white_urls.large }}" alt="{{ client.name }}" />
```

### **Chargement lazy avec JavaScript**
```javascript
// Récupérer le portfolio
fetch('/projects/api/portfolio/?featured=true')
  .then(response => response.json())
  .then(data => {
    data.projects.forEach(project => {
      // Utiliser project.image_urls.thumbnail pour les cartes
      // Utiliser project.image_urls.large pour les modales
    });
  });
```

## 🎯 **Optimisations performance**

### **Cache et CDN**
- Images servies via Cloudinary CDN
- Cache automatique des transformations
- Compression lossless et lossy intelligente

### **Formats adaptatifs**
- WebP automatique pour les navigateurs compatibles
- AVIF pour les navigateurs très récents
- Fallback JPEG/PNG pour compatibilité

### **Lazy loading**
- `loading="lazy"` sur toutes les images non critiques
- Intersection Observer pour contrôle avancé
- Placeholder base64 pour transitions fluides

## 🔐 **Authentification et permissions**

### **APIs publiques**
- `/api/portfolio/` : Projets publiés uniquement
- `/api/clients/` : Clients actifs uniquement  
- `/api/categories/` : Toutes les catégories
- `/api/{slug}/images/` : Images des projets publiés

### **APIs protégées** (admin uniquement)
- `/api/stats/` : Statistiques complètes
- Projets en brouillon dans les stats
- Données clients sensibles

## 🚀 **Exemples d'intégration**

### **React/Vue.js**
```javascript
const useProjects = (filters = {}) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const params = new URLSearchParams(filters);
    fetch(`/projects/api/portfolio/?${params}`)
      .then(res => res.json())
      .then(data => {
        setProjects(data.projects);
        setLoading(false);
      });
  }, [filters]);
  
  return { projects, loading };
};
```

### **Alpine.js**
```html
<div x-data="{ 
  projects: [], 
  loading: true,
  async loadProjects() {
    const response = await fetch('/projects/api/portfolio/');
    const data = await response.json();
    this.projects = data.projects;
    this.loading = false;
  }
}" x-init="loadProjects()">
  
  <template x-for="project in projects">
    <div class="project-card">
      <img :src="project.image_urls.thumbnail" :alt="project.title" />
      <h3 x-text="project.title"></h3>
    </div>
  </template>
</div>
```

## 📊 **Codes de réponse HTTP**

- `200 OK` : Requête réussie
- `404 Not Found` : Projet/client/catégorie introuvable
- `500 Internal Server Error` : Erreur serveur

## 🔄 **Versioning**

L'API suit le versioning sémantique. Les changements majeurs seront préfixés par version :
- `/api/v1/portfolio/` (future version)
- `/api/portfolio/` (version actuelle, stable)

---

*Documentation mise à jour le 26 juin 2025*
