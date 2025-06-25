from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.utils import timezone
from authentication.models import UserSession

User = get_user_model()


class Command(BaseCommand):
    help = "Synchronize existing Django sessions with UserSession tracking"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreation of existing UserSessions",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]

        self.stdout.write("🔄 Synchronisation des sessions Django avec UserSession...")

        # Obtenir toutes les sessions Django actives avec des utilisateurs
        active_sessions = Session.objects.filter(expire_date__gt=timezone.now())

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for session in active_sessions:
            session_data = session.get_decoded()
            user_id = session_data.get("_auth_user_id")

            if not user_id:
                # Session anonyme, ignorer
                continue

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ Utilisateur {user_id} introuvable pour session {session.session_key}"
                    )
                )
                continue

            # Vérifier si UserSession existe déjà
            existing_user_session = UserSession.objects.filter(session=session).first()

            if existing_user_session and not force:
                skipped_count += 1
                continue

            if dry_run:
                if existing_user_session:
                    self.stdout.write(f"📝 MISE À JOUR: Session pour {user.email}")
                else:
                    self.stdout.write(
                        f"📝 CRÉATION: Nouvelle session pour {user.email}"
                    )
                created_count += 1
                continue

            # Créer ou mettre à jour UserSession
            defaults = {
                "user": user,
                "ip_address": "127.0.0.1",  # IP par défaut pour les sessions existantes
                "user_agent": "Unknown (synchronized session)",
                "login_method": "password",
                "is_active": True,
                "created_at": session.expire_date
                - timezone.timedelta(seconds=3600),  # Estimation
                "last_activity": timezone.now(),
                "country": "",
                "city": "",
                "is_suspicious": False,
            }

            if existing_user_session and force:
                # Mettre à jour
                for key, value in defaults.items():
                    if key != "user":  # Ne pas changer l'utilisateur
                        setattr(existing_user_session, key, value)
                existing_user_session.save()
                updated_count += 1
                self.stdout.write(f"🔄 Mise à jour: Session pour {user.email}")
            else:
                # Créer
                user_session = UserSession.objects.create(session=session, **defaults)
                created_count += 1
                self.stdout.write(f"✅ Création: Nouvelle session pour {user.email}")

        # Résumé
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"\n📋 MODE DRY-RUN - Aucune modification effectuée")
            )

        self.stdout.write(f"\n📊 Résumé:")
        self.stdout.write(f"  ✅ Sessions créées: {created_count}")
        self.stdout.write(f"  🔄 Sessions mises à jour: {updated_count}")
        self.stdout.write(f"  ⏭️ Sessions ignorées: {skipped_count}")

        # Nettoyer les sessions expirées
        if not dry_run:
            expired_user_sessions = UserSession.objects.filter(
                session__expire_date__lt=timezone.now(), is_active=True
            )
            expired_count = expired_user_sessions.count()
            expired_user_sessions.update(is_active=False)

            if expired_count > 0:
                self.stdout.write(
                    f"🧹 {expired_count} sessions expirées marquées comme inactives"
                )

        self.stdout.write(self.style.SUCCESS("✅ Synchronisation terminée!"))
