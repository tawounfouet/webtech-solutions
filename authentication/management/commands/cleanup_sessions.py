from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from authentication.models import UserSession


class Command(BaseCommand):
    help = "Clean up expired user sessions and inactive session records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Remove sessions older than this many days (default: 30)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]

        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        self.stdout.write(f"Cleaning up sessions older than {days} days...")

        # Find expired Django sessions
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        expired_count = expired_sessions.count()

        # Find old UserSession records
        old_user_sessions = UserSession.objects.filter(created_at__lt=cutoff_date)
        old_user_sessions_count = old_user_sessions.count()

        # Find inactive UserSession records
        inactive_sessions = UserSession.objects.filter(
            is_active=False, last_activity__lt=cutoff_date
        )
        inactive_count = inactive_sessions.count()

        if dry_run:
            self.stdout.write(self.style.WARNING(f"DRY RUN - Would delete:"))
            self.stdout.write(f"  - {expired_count} expired Django sessions")
            self.stdout.write(f"  - {old_user_sessions_count} old UserSession records")
            self.stdout.write(f"  - {inactive_count} inactive UserSession records")
            return

        # Mark UserSessions as inactive for expired Django sessions
        user_sessions_to_deactivate = UserSession.objects.filter(
            session__in=expired_sessions, is_active=True
        )
        deactivated_count = user_sessions_to_deactivate.update(is_active=False)

        # Delete expired Django sessions
        expired_sessions.delete()

        # Delete old UserSession records
        old_user_sessions.delete()

        # Delete inactive UserSession records
        inactive_sessions.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully cleaned up:\n"
                f"  - {expired_count} expired Django sessions\n"
                f"  - {deactivated_count} UserSessions marked as inactive\n"
                f"  - {old_user_sessions_count} old UserSession records deleted\n"
                f"  - {inactive_count} inactive UserSession records deleted"
            )
        )
