#!/usr/bin/env python
"""
Script pour créer des données de test avec du contenu CKEditor5
"""
import os
import sys
import django

# Ajouter le chemin du projet
sys.path.append('/workspaces/webtech-solutions')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from projects.models import Project, ProjectCategory, Client, ProjectMetrics, ProjectTestimonial

def create_sample_content():
    """Créer du contenu d'exemple avec du HTML riche (CKEditor5)"""
    
    # Contenu CKEditor5 avec du HTML riche
    sample_content = """
    <h2>Objectifs du projet</h2>
    <p>Ce projet avait pour objectif de <strong>moderniser complètement</strong> l'identité visuelle et l'expérience utilisateur de notre client. Les défis principaux étaient :</p>
    <ul>
        <li>Améliorer l'<em>engagement utilisateur</em> de 150%</li>
        <li>Optimiser les <strong>performances web</strong> pour un meilleur référencement</li>
        <li>Créer une interface <strong>responsive</strong> et accessible</li>
    </ul>
    
    <h3>Méthodologie appliquée</h3>
    <p>Notre approche s'est basée sur les meilleures pratiques du <strong>design thinking</strong> :</p>
    <ol>
        <li><strong>Recherche utilisateur</strong> - Interviews et analyses comportementales</li>
        <li><strong>Prototypage rapide</strong> - Création de maquettes interactives</li>
        <li><strong>Tests utilisateurs</strong> - Validation des concepts avec les utilisateurs finaux</li>
        <li><strong>Développement itératif</strong> - Mise en place par sprints agiles</li>
    </ol>
    
    <blockquote>
        <p>"L'innovation distingue un leader d'un suiveur" - Steve Jobs</p>
    </blockquote>
    
    <h3>Technologies utilisées</h3>
    <p>Pour ce projet, nous avons fait appel à une stack technologique moderne :</p>
    <table>
        <thead>
            <tr>
                <th>Domaine</th>
                <th>Technologie</th>
                <th>Avantages</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Frontend</td>
                <td>React.js + TypeScript</td>
                <td>Performance et maintenabilité</td>
            </tr>
            <tr>
                <td>Backend</td>
                <td>Django + PostgreSQL</td>
                <td>Robustesse et sécurité</td>
            </tr>
            <tr>
                <td>Design</td>
                <td>Figma + Adobe Creative Suite</td>
                <td>Collaboration et créativité</td>
            </tr>
        </tbody>
    </table>
    
    <h3>Résultats obtenus</h3>
    <p>Les résultats de ce projet ont dépassé toutes nos attentes. L'impact a été immédiat et mesurable sur tous les KPIs définis :</p>
    
    <p>Le nouveau design a permis d'améliorer significativement l'expérience utilisateur, avec une interface plus <strong>intuitive</strong> et des parcours utilisateurs optimisés.</p>
    
    <p>Code d'exemple pour l'optimisation des performances :</p>
    <pre><code>// Lazy loading des images
const LazyImage = ({ src, alt }) => {
  return (
    &lt;img 
      src={src} 
      alt={alt} 
      loading="lazy"
      className="optimized-image"
    /&gt;
  );
};</code></pre>
    """
    
    return sample_content

def update_projects_with_content():
    """Mettre à jour les projets existants avec du contenu riche"""
    
    projects = Project.objects.all()
    content = create_sample_content()
    
    for project in projects:
        if not project.content or project.content.strip() == "":
            project.content = content
            project.save()
            print(f"✅ Contenu ajouté au projet: {project.title}")
        else:
            print(f"⏭️  Projet déjà avec contenu: {project.title}")

def create_sample_metrics():
    """Créer des métriques d'exemple pour les projets"""
    
    projects_without_metrics = Project.objects.filter(metrics__isnull=True)
    
    for project in projects_without_metrics:
        metrics = ProjectMetrics.objects.create(
            project=project,
            page_views_increase=150.0,
            conversion_rate_increase=75.0,
            bounce_rate_decrease=45.0,
            loading_time_improvement=65.0,
            seo_score=95,
            accessibility_score=98,
            performance_score=92,
            leads_increase=120.0
        )
        print(f"✅ Métriques créées pour: {project.title}")

def create_sample_testimonials():
    """Créer des témoignages d'exemple"""
    
    testimonials_data = [
        {
            "client_name": "Marie Dubois",
            "client_position": "Directrice Marketing",
            "quote": "WebTech Solutions a complètement transformé notre présence en ligne. L'équipe est professionnelle, créative et toujours à l'écoute de nos besoins. Les résultats ont dépassé nos attentes !",
            "rating": 5
        },
        {
            "client_name": "Pierre Martin",
            "client_position": "CEO",
            "quote": "Un travail exceptionnel ! Notre nouveau site web nous a permis d'augmenter nos conversions de 200%. Je recommande vivement cette équipe.",
            "rating": 5
        },
        {
            "client_name": "Sarah Johnson",
            "client_position": "Responsable Digital",
            "quote": "Collaboration fluide, délais respectés et résultat final parfait. WebTech Solutions maîtrise parfaitement les dernières technologies.",
            "rating": 4
        }
    ]
    
    projects_without_testimonials = Project.objects.filter(testimonial__isnull=True)[:3]
    
    for i, project in enumerate(projects_without_testimonials):
        if i < len(testimonials_data):
            testimonial_data = testimonials_data[i]
            testimonial = ProjectTestimonial.objects.create(
                project=project,
                **testimonial_data
            )
            print(f"✅ Témoignage créé pour: {project.title}")

if __name__ == '__main__':
    print("🚀 Création du contenu d'exemple...")
    
    print("\n📝 Mise à jour des projets avec du contenu CKEditor5...")
    update_projects_with_content()
    
    print("\n📊 Création des métriques d'exemple...")
    create_sample_metrics()
    
    print("\n💬 Création des témoignages d'exemple...")
    create_sample_testimonials()
    
    print("\n✅ Contenu d'exemple créé avec succès !")
    print("🌐 Vous pouvez maintenant tester la page de détail des projets.")
