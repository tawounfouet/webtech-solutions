from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from projects.models import (
    ProjectCategory, 
    Client, 
    Project, 
    ProjectImage, 
    ProjectTestimonial,
    ProjectMetrics,
    ProjectStatus
)
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Crée des données initiales pour les projets basées sur les templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les données existantes avant de créer les nouvelles',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Suppression des données existantes...'))
            Project.objects.all().delete()
            Client.objects.all().delete()
            ProjectCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Données supprimées avec succès.'))

        self.stdout.write('Création des données initiales...')

        # Créer les catégories de projets
        categories = self.create_categories()
        
        # Créer les clients
        clients = self.create_clients()
        
        # Créer les projets
        projects = self.create_projects(categories, clients)
        
        # Créer les témoignages
        self.create_testimonials(projects)
        
        # Créer les métriques
        self.create_metrics(projects)

        self.stdout.write(
            self.style.SUCCESS(
                f'Données créées avec succès!\n'
                f'- {len(categories)} catégories\n'
                f'- {len(clients)} clients\n'
                f'- {len(projects)} projets'
            )
        )

    def create_categories(self):
        """Crée les catégories de projets basées sur les services du template"""
        categories_data = [
            {
                'name': 'Digital Marketing',
                'description': 'Growing brands online through digital channels.',
                'color': '#007bff'
            },
            {
                'name': 'Product Design',
                'description': 'Creating products that users love and businesses need.',
                'color': '#28a745'
            },
            {
                'name': 'Web Design',
                'description': 'Designing websites that are visually appealing & user-friendly.',
                'color': '#17a2b8'
            },
            {
                'name': 'Development',
                'description': 'Building robust and scalable web applications.',
                'color': '#ffc107'
            },
            {
                'name': 'Branding',
                'description': 'Creating strong brand identities that resonate.',
                'color': '#dc3545'
            },
            {
                'name': 'UI/UX Design',
                'description': 'Crafting intuitive user experiences and interfaces.',
                'color': '#6f42c1'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = ProjectCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Catégorie créée: {category.name}')

        return categories

    def create_clients(self):
        """Crée les clients fictifs"""
        clients_data = [
            {
                'name': 'TechStart Solutions',
                'description': 'Une startup technologique innovante spécialisée dans les solutions cloud.',
                'website': 'https://techstart-solutions.com'
            },
            {
                'name': 'Green Energy Corp',
                'description': 'Leader dans les solutions d\'énergie renouvelable.',
                'website': 'https://greenenergy-corp.com'
            },
            {
                'name': 'Digital Health',
                'description': 'Plateforme de santé numérique révolutionnaire.',
                'website': 'https://digital-health.fr'
            },
            {
                'name': 'EcoMarket',
                'description': 'Marketplace dédiée aux produits écologiques.',
                'website': 'https://ecomarket.fr'
            },
            {
                'name': 'FinanceFlow',
                'description': 'Application de gestion financière pour PME.',
                'website': 'https://financeflow.com'
            },
            {
                'name': 'EduTech Academy',
                'description': 'Plateforme d\'apprentissage en ligne innovante.',
                'website': 'https://edutech-academy.fr'
            }
        ]

        clients = []
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                name=client_data['name'],
                defaults={
                    'description': client_data['description'],
                    'website': client_data['website'],
                    'is_active': True
                }
            )
            clients.append(client)
            if created:
                self.stdout.write(f'Client créé: {client.name}')

        return clients

    def create_projects(self, categories, clients):
        """Crée les projets basés sur le template portfolio"""
        projects_data = [
            {
                'title': 'Transforming Ideas into Reality',
                'subtitle': 'Une plateforme web innovante pour TechStart Solutions',
                'description': 'Développement d\'une application web complète avec interface moderne et backend robuste pour optimiser les processus métier.',
                'content': self.get_project_content_1(),
                'client': clients[0],
                'categories': [categories[0], categories[3]],  # Digital Marketing, Development
                'status': ProjectStatus.COMPLETED,
                'start_date': date(2024, 1, 15),
                'end_date': date(2024, 4, 30),
                'budget': 45000.00,
                'is_featured': True,
                'is_published': True,
                'order': 1
            },
            {
                'title': 'Green Energy Revolution',
                'subtitle': 'Refonte complète de l\'identité visuelle et digitale',
                'description': 'Création d\'une nouvelle identité de marque et développement d\'un site web moderne pour Green Energy Corp.',
                'content': self.get_project_content_2(),
                'client': clients[1],
                'categories': [categories[4], categories[2]],  # Branding, Web Design
                'status': ProjectStatus.COMPLETED,
                'start_date': date(2024, 2, 1),
                'end_date': date(2024, 5, 15),
                'budget': 35000.00,
                'is_featured': True,
                'is_published': True,
                'order': 2
            },
            {
                'title': 'Digital Health Platform',
                'subtitle': 'Application mobile et web pour la santé connectée',
                'description': 'Conception et développement d\'une plateforme complète de santé numérique avec interface patient et professionnel.',
                'content': self.get_project_content_3(),
                'client': clients[2],
                'categories': [categories[5], categories[3], categories[1]],  # UI/UX, Development, Product Design
                'status': ProjectStatus.COMPLETED,
                'start_date': date(2024, 3, 1),
                'end_date': date(2024, 7, 30),
                'budget': 75000.00,
                'is_featured': True,
                'is_published': True,
                'order': 3
            },
            {
                'title': 'EcoMarket E-commerce',
                'subtitle': 'Marketplace responsable et durable',
                'description': 'Création d\'une marketplace innovante dédiée aux produits écologiques avec système de paiement intégré.',
                'content': self.get_project_content_4(),
                'client': clients[3],
                'categories': [categories[2], categories[3], categories[0]],  # Web Design, Development, Digital Marketing
                'status': ProjectStatus.COMPLETED,
                'start_date': date(2024, 4, 1),
                'end_date': date(2024, 8, 15),
                'budget': 55000.00,
                'is_featured': False,
                'is_published': True,
                'order': 4
            },
            {
                'title': 'FinanceFlow Dashboard',
                'subtitle': 'Tableau de bord financier intelligent',
                'description': 'Interface de gestion financière avancée avec analytics en temps réel et reporting automatisé.',
                'content': self.get_project_content_5(),
                'client': clients[4],
                'categories': [categories[5], categories[3]],  # UI/UX, Development
                'status': ProjectStatus.IN_PROGRESS,
                'start_date': date(2024, 6, 1),
                'end_date': date(2024, 12, 30),
                'budget': 65000.00,
                'is_featured': False,
                'is_published': True,
                'order': 5
            },
            {
                'title': 'EduTech Learning Platform',
                'subtitle': 'Plateforme d\'apprentissage nouvelle génération',
                'description': 'Développement d\'une plateforme éducative interactive avec système de gamification et suivi personnalisé.',
                'content': self.get_project_content_6(),
                'client': clients[5],
                'categories': [categories[1], categories[3], categories[5]],  # Product Design, Development, UI/UX
                'status': ProjectStatus.DRAFT,
                'start_date': date(2024, 8, 1),
                'end_date': date(2025, 2, 28),
                'budget': 85000.00,
                'is_featured': False,
                'is_published': False,
                'order': 6
            }
        ]

        projects = []
        for project_data in projects_data:
            # Créer le projet
            project, created = Project.objects.get_or_create(
                title=project_data['title'],
                defaults={
                    'subtitle': project_data['subtitle'],
                    'description': project_data['description'],
                    'content': project_data['content'],
                    'client': project_data['client'],
                    'status': project_data['status'],
                    'start_date': project_data['start_date'],
                    'end_date': project_data['end_date'],
                    'budget': project_data['budget'],
                    'is_featured': project_data['is_featured'],
                    'is_published': project_data['is_published'],
                    'order': project_data['order'],
                    'published_at': timezone.now() if project_data['is_published'] else None
                }
            )
            
            if created:
                # Ajouter les catégories
                project.categories.set(project_data['categories'])
                projects.append(project)
                self.stdout.write(f'Projet créé: {project.title}')

        return projects

    def create_testimonials(self, projects):
        """Crée les témoignages pour les projets"""
        testimonials_data = [
            {
                'client_name': 'Sarah Martin',
                'client_position': 'CEO, TechStart Solutions',
                'quote': 'L\'équipe de Webtech Solutions a transformé notre vision en une réalité dépassant toutes nos attentes. Leur expertise technique et leur approche collaborative ont été exceptionnelles.',
                'rating': 5
            },
            {
                'client_name': 'Marc Dubois',
                'client_position': 'Directeur Marketing, Green Energy Corp',
                'quote': 'Un travail remarquable sur notre nouvelle identité de marque. Ils ont parfaitement saisi notre mission environnementale et l\'ont traduite visuellement.',
                'rating': 5
            },
            {
                'client_name': 'Dr. Émilie Rousseau',
                'client_position': 'Fondatrice, Digital Health',
                'quote': 'La plateforme développée révolutionne notre approche de la santé connectée. Interface intuitive et performance technique au rendez-vous.',
                'rating': 5
            }
        ]

        for i, testimonial_data in enumerate(testimonials_data):
            if i < len(projects):
                testimonial, created = ProjectTestimonial.objects.get_or_create(
                    project=projects[i],
                    defaults={
                        'client_name': testimonial_data['client_name'],
                        'client_position': testimonial_data['client_position'],
                        'quote': testimonial_data['quote'],
                        'rating': testimonial_data['rating'],
                        'is_featured': True
                    }
                )
                if created:
                    self.stdout.write(f'Témoignage créé pour: {projects[i].title}')

    def create_metrics(self, projects):
        """Crée les métriques pour les projets terminés"""
        metrics_data = [
            {
                'page_views_increase': 245.5,
                'conversion_rate_increase': 78.3,
                'bounce_rate_decrease': 45.2,
                'loading_time_improvement': 67.8,
                'revenue_increase': 125000.00,
                'leads_increase': 156.7,
                'seo_score': 95,
                'accessibility_score': 98,
                'performance_score': 92
            },
            {
                'page_views_increase': 189.2,
                'conversion_rate_increase': 92.1,
                'bounce_rate_decrease': 38.5,
                'loading_time_improvement': 72.3,
                'revenue_increase': 89000.00,
                'leads_increase': 134.2,
                'seo_score': 93,
                'accessibility_score': 96,
                'performance_score': 89
            },
            {
                'page_views_increase': 312.8,
                'conversion_rate_increase': 145.6,
                'bounce_rate_decrease': 52.1,
                'loading_time_improvement': 81.4,
                'revenue_increase': 198000.00,
                'leads_increase': 267.3,
                'seo_score': 97,
                'accessibility_score': 99,
                'performance_score': 94
            }
        ]

        completed_projects = [p for p in projects if p.status == ProjectStatus.COMPLETED]
        for i, project in enumerate(completed_projects[:3]):
            metrics, created = ProjectMetrics.objects.get_or_create(
                project=project,
                defaults=metrics_data[i]
            )
            if created:
                self.stdout.write(f'Métriques créées pour: {project.title}')

    def get_project_content_1(self):
        return """
        <h4>Vue d'ensemble</h4>
        <p class="lead">TechStart Solutions avait besoin d'une plateforme web moderne pour optimiser leurs processus métier et améliorer l'expérience client.</p>
        
        <p>Le projet consistait à développer une application web complète avec une interface utilisateur moderne et un backend robuste. L'objectif était de créer une solution qui non seulement répondrait aux besoins actuels de l'entreprise, mais qui pourrait également évoluer avec leur croissance.</p>
        
        <h4>Le Défi</h4>
        <p>Le principal défi était d'intégrer plusieurs systèmes existants tout en créant une interface unifiée et intuitive. Il fallait également garantir des performances optimales et une sécurité de niveau entreprise.</p>
        
        <ul>
            <li>Intégration de systèmes legacy</li>
            <li>Interface utilisateur moderne et responsive</li>
            <li>Performance et sécurité</li>
            <li>Évolutivité de la solution</li>
        </ul>
        
        <h4>Solution</h4>
        <p>Nous avons développé une architecture modulaire utilisant les dernières technologies web, permettant une intégration fluide et une maintenance simplifiée.</p>
        """

    def get_project_content_2(self):
        return """
        <h4>Vue d'ensemble</h4>
        <p class="lead">Green Energy Corp souhaitait moderniser son identité visuelle pour mieux refléter ses valeurs environnementales et sa position de leader dans les énergies renouvelables.</p>
        
        <p>Ce projet englobait la refonte complète de l'identité de marque, la création d'un nouveau site web et le développement d'une stratégie de communication digitale cohérente.</p>
        
        <h4>Le Défi</h4>
        <p>L'enjeu était de créer une identité forte qui transmette à la fois l'innovation technologique et l'engagement environnemental de l'entreprise.</p>
        
        <h4>Résultat</h4>
        <p>Une nouvelle identité de marque moderne et engageante, accompagnée d'un site web performant qui a généré une augmentation significative de l'engagement client.</p>
        """

    def get_project_content_3(self):
        return """
        <h4>Vue d'ensemble</h4>
        <p class="lead">Digital Health révolutionne l'accès aux soins de santé grâce à une plateforme numérique innovante connectant patients et professionnels de santé.</p>
        
        <p>Le projet comprenait le développement d'applications mobiles et web, avec des interfaces distinctes pour les patients et les professionnels de santé, tout en respectant les standards de sécurité médicale.</p>
        
        <h4>Le Défi</h4>
        <p>Créer une plateforme sécurisée et conforme aux réglementations de santé, tout en maintenant une expérience utilisateur fluide et intuitive.</p>
        """

    def get_project_content_4(self):
        return """
        <h4>Vue d'ensemble</h4>
        <p class="lead">EcoMarket est une marketplace innovante dédiée aux produits écologiques et durables, connectant consommateurs responsables et producteurs éthiques.</p>
        
        <p>Le projet incluait le développement d'une plateforme e-commerce complète avec système de paiement sécurisé, gestion des stocks et tableau de bord marchand.</p>
        """

    def get_project_content_5(self):
        return """
        <h4>Vue d'ensemble</h4>
        <p class="lead">FinanceFlow offre aux PME un tableau de bord financier intelligent avec analytics en temps réel et reporting automatisé.</p>
        
        <p>L'interface développée permet une gestion financière simplifiée avec des insights précieux pour la prise de décision stratégique.</p>
        """

    def get_project_content_6(self):
        return """
        <h4>Vue d'ensemble</h4>
        <p class="lead">EduTech Academy propose une plateforme d'apprentissage nouvelle génération avec gamification et suivi personnalisé.</p>
        
        <p>Le projet vise à révolutionner l'éducation en ligne grâce à des technologies innovantes et une approche pédagogique moderne.</p>
        """
