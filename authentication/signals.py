import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.utils import timezone
from .models import UserSession
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    """
    Signal handler for when a user logs in.
    Creates or updates UserSession with login information.
    """
    try:
        # Make sure session exists
        if not hasattr(request, "session") or not request.session.session_key:
            request.session.save()  # Force session creation

        # Get the Django session object
        session_obj = Session.objects.get(session_key=request.session.session_key)

        # Get client information
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        login_method = get_login_method(request)

        # Create or update UserSession
        user_session, created = UserSession.objects.get_or_create(
            session=session_obj,
            defaults={
                "user": user,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "login_method": login_method,
                "is_active": True,
            },
        )

        if not created:
            # Update existing session
            user_session.user = user
            user_session.ip_address = ip_address
            user_session.user_agent = user_agent
            user_session.login_method = login_method
            user_session.is_active = True
            user_session.last_activity = timezone.now()
            user_session.save()

        # Log successful login
        logger.info(f"User {user.email} logged in from {ip_address}")

        # Store session info in Django session for later use
        request.session["user_session_id"] = user_session.id
        request.session["login_ip"] = ip_address
        request.session["login_time"] = timezone.now().isoformat()

    except Session.DoesNotExist:
        logger.error(f"Session not found during login for user {user.email}")
    except Exception as e:
        logger.error(f"Error handling user login signal: {e}")


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    """
    Signal handler for when a user logs out.
    Marks UserSession as inactive.
    """
    try:
        # Get session info from Django session
        user_session_id = request.session.get("user_session_id")

        if user_session_id:
            # Mark specific UserSession as inactive
            UserSession.objects.filter(id=user_session_id).update(
                is_active=False, last_activity=timezone.now()
            )
        elif hasattr(request, "session") and request.session.session_key:
            # Fallback: find by session key
            try:
                session_obj = Session.objects.get(
                    session_key=request.session.session_key
                )
                UserSession.objects.filter(session=session_obj).update(
                    is_active=False, last_activity=timezone.now()
                )
            except Session.DoesNotExist:
                pass

        # Log logout
        if user:
            logger.info(f"User {user.email} logged out")

    except Exception as e:
        logger.error(f"Error handling user logout signal: {e}")


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a user is created.
    Optionally creates a basic session for tracking purposes.
    Only for users created outside of web requests (shell, management commands).
    """
    if created and not hasattr(instance, "_skip_session_creation"):
        try:
            # Check if this is a shell/script creation (no active request)
            from django.core.management import get_random_secret_key
            from django.contrib.sessions.backends.db import SessionStore
            from django.contrib.sessions.models import Session

            # Only create session for superusers/staff created via shell
            if instance.is_superuser or instance.is_staff:
                logger.info(
                    f"Creating basic session for shell-created user: {instance.email}"
                )

                # Create a basic session
                session = SessionStore()
                session["_auth_user_id"] = str(instance.id)
                session["_auth_user_backend"] = (
                    "django.contrib.auth.backends.ModelBackend"
                )
                session.save()

                session_obj = Session.objects.get(session_key=session.session_key)

                # Create UserSession
                UserSession.objects.create(
                    user=instance,
                    session=session_obj,
                    ip_address="127.0.0.1",  # Local creation
                    user_agent="Shell/Management Command",
                    login_method="shell",
                    country="Local",
                    city="Development",
                    is_active=True,
                )

                logger.info(f"Basic session created for {instance.email}")

        except Exception as e:
            logger.error(f"Error creating session for new user {instance.email}: {e}")


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
    return ip


def get_user_agent(request):
    """Extract user agent from request."""
    return request.META.get("HTTP_USER_AGENT", "")[:1000]  # Limit length


def get_login_method(request):
    """Determine login method from session/request."""
    # Check for social auth backends
    if hasattr(request, "session"):
        backend = request.session.get("social_auth_last_login_backend")
        if backend:
            if "google" in backend.lower():
                return "google"
            elif "facebook" in backend.lower():
                return "facebook"
            elif "github" in backend.lower():
                return "github"
            elif "linkedin" in backend.lower():
                return "linkedin"
            else:
                return "social"

        # Check for OAuth indicators
        if request.session.get("oauth_login"):
            return "oauth"

        # Check for API login
        if request.session.get("api_login"):
            return "api"

    # Check request headers for API authentication
    if request.META.get("HTTP_AUTHORIZATION"):
        auth_header = request.META["HTTP_AUTHORIZATION"]
        if auth_header.startswith("Bearer "):
            return "token"
        elif auth_header.startswith("Token "):
            return "api_token"

    # Default to password-based login
    return "password"
