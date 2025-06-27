import os
import re
import random
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from django.utils import timezone
from cloudinary.uploader import upload
from projects.models import Project, Client, ProjectCategory, ProjectStatus
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Crée des projets à partir des images dans un dossier spécifié"

    def add_arguments(self, parser):
        parser.add_argument(
            "--directory",
            type=str,
            required=False,
            help="Chemin du dossier contenant les images (optionnel)",
        )
        parser.add_argument(
            "--client-id",
            type=int,
            required=False,
            help="ID du client à associer aux projets (optionnel)",
        )
        parser.add_argument(
            "--category-id",
            type=int,
            required=False,
            help="ID de la catégorie à associer aux projets (optionnel)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Exécute sans créer les projets (mode test)",
        )

    def handle(self, *args, **options):
        # Définir le dossier d'images par défaut (dans le même répertoire que ce script)
        script_dir = Path(__file__).parent
        default_dir = script_dir / "projects-featured-images"

        # Utiliser le dossier spécifié ou le dossier par défaut
        directory_path = options.get("directory") or str(default_dir)
        client_id = options.get("client_id")
        category_id = options.get("category_id")
        dry_run = options.get("dry_run", False)

        # Vérifier que le dossier existe
        if not os.path.isdir(directory_path):
            self.stderr.write(
                self.style.ERROR(f"Le dossier '{directory_path}' n'existe pas.")
            )
            return

        # Récupérer tous les clients disponibles ou celui spécifié
        clients = []
        if client_id:
            try:
                client = Client.objects.get(pk=client_id)
                clients = [client]
                self.stdout.write(
                    self.style.SUCCESS(f"Utilisation du client spécifié: {client.name}")
                )
            except Client.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Le client avec l'ID {client_id} n'existe pas.")
                )
                return
        else:
            clients = list(Client.objects.filter(is_active=True))
            if not clients:
                self.stderr.write(
                    self.style.ERROR("Aucun client actif trouvé en base de données.")
                )
                return
            self.stdout.write(
                self.style.SUCCESS(
                    f"Trouvé {len(clients)} clients disponibles pour sélection aléatoire."
                )
            )

        # Récupérer toutes les catégories disponibles ou celle spécifiée
        categories = []
        if category_id:
            try:
                category = ProjectCategory.objects.get(pk=category_id)
                categories = [category]
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Utilisation de la catégorie spécifiée: {category.name}"
                    )
                )
            except ProjectCategory.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        f"La catégorie avec l'ID {category_id} n'existe pas."
                    )
                )
                return
        else:
            categories = list(ProjectCategory.objects.all())
            if not categories:
                self.stderr.write(
                    self.style.WARNING("Aucune catégorie trouvée en base de données.")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Trouvé {len(categories)} catégories disponibles pour sélection aléatoire."
                    )
                )

        # Liste des extensions d'image autorisées
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

        # Liste des images dans le dossier
        image_files = [
            f
            for f in os.listdir(directory_path)
            if any(f.lower().endswith(ext) for ext in allowed_extensions)
        ]

        if not image_files:
            self.stderr.write(
                self.style.WARNING(
                    f"Aucune image trouvée dans le dossier '{directory_path}'."
                )
            )
            return

        self.stdout.write(self.style.SUCCESS(f"Trouvé {len(image_files)} images."))

        # Créer un projet pour chaque image
        projects_created = 0

        for image_file in image_files:
            # Extraire le nom du projet à partir du nom du fichier
            # Enlever les 5 premiers caractères (home_) et l'extension (.jpg, .png, etc.)
            file_name = os.path.splitext(image_file)[0]  # Nom sans extension

            # Vérifier si le nom commence par 'home_' et l'enlever
            if file_name.startswith("home_"):
                project_name = file_name[5:]  # Enlever les 5 premiers caractères
            else:
                project_name = file_name

            # Convertir le nom en titre approprié (première lettre en majuscule, remplacer les underscores par des espaces)
            project_name = project_name.replace("_", " ").title()

            # Générer un slug unique
            base_slug = slugify(project_name)
            slug = base_slug
            counter = 1

            # Vérifier si le slug existe déjà et générer un nouveau si nécessaire
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Sélectionner un client aléatoire
            selected_client = random.choice(clients)
            self.stdout.write(
                f"Traitement de l'image '{image_file}' -> Projet: '{project_name}' -> Client: '{selected_client.name}'"
            )

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"[DRY RUN] Projet '{project_name}' serait créé avec le slug '{slug}' et le client '{selected_client.name}'"
                    )
                )
                continue

            # Créer le projet
            try:
                # Créer un nouveau projet
                project = Project(
                    title=project_name,
                    slug=slug,
                    description=f"Description pour le projet {project_name}",
                    content=f"<h2>Contenu détaillé pour {project_name}</h2><p>Ce contenu peut être modifié ultérieurement.</p>",
                    client=selected_client,
                    status=ProjectStatus.DRAFT,
                    is_published=False,
                    order=0,
                )
                project.save()

                # Ajouter des catégories aléatoires (entre 1 et 3)
                if categories:
                    # Si une catégorie spécifique a été demandée, utiliser uniquement celle-là
                    if category_id:
                        project.categories.add(categories[0])
                        self.stdout.write(
                            f"  - Catégorie ajoutée: {categories[0].name}"
                        )
                    else:
                        # Sinon, sélectionner entre 1 et 3 catégories aléatoires
                        num_categories = min(random.randint(1, 3), len(categories))
                        selected_categories = random.sample(categories, num_categories)
                        for cat in selected_categories:
                            project.categories.add(cat)
                            self.stdout.write(f"  - Catégorie ajoutée: {cat.name}")

                # Charger l'image sur Cloudinary et l'associer au projet
                image_path = os.path.join(directory_path, image_file)

                # Télécharger l'image sur Cloudinary
                with open(image_path, "rb") as img_file:
                    # Upload vers Cloudinary
                    upload_result = upload(
                        img_file,
                        folder="projects/featured/original",
                        public_id=f"{slug}_original",
                        resource_type="image",
                    )

                    project.featured_image_cloudinary_public_id = upload_result[
                        "public_id"
                    ]
                    project.featured_image = upload_result["secure_url"]

                    # Générer les versions optimisées
                    project.generate_image_versions()

                # Sauvegarder le projet avec l'image
                project.save()

                projects_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Projet '{project_name}' créé avec succès (ID: {project.id})"
                    )
                )

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Erreur lors de la création du projet pour l'image '{image_file}': {str(e)}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Création terminée. {projects_created} projets créés sur {len(image_files)} images."
            )
        )
