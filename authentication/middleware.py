import logging
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .models import UserSession

# Try to import GeoIP2, but handle if it's not available
try:
    from django.contrib.gis.geoip2 import GeoIP2

    GEOIP2_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    GEOIP2_AVAILABLE = False
    GeoIP2 = None

logger = logging.getLogger(__name__)


class UserSessionTrackingMiddleware:
    """
    Middleware to automatically track user sessions for security and monitoring.
    Creates and updates UserSession objects based on Django sessions.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request before view
        self.process_request(request)

        # Get response from view
        response = self.get_response(request)

        # Process response after view
        self.process_response(request, response)

        return response

    def process_request(self, request):
        """Process incoming request to track session information."""
        # Only track authenticated users
        if not request.user.is_authenticated:
            return

        # Skip if session doesn't exist yet
        if not hasattr(request, "session") or not request.session.session_key:
            return

        try:
            # Get or create UserSession
            session_obj = Session.objects.get(session_key=request.session.session_key)
            user_session, created = UserSession.objects.get_or_create(
                session=session_obj,
                defaults={
                    "user": request.user,
                    "ip_address": self.get_client_ip(request),
                    "user_agent": self.get_user_agent(request),
                    "login_method": self.get_login_method(request),
                },
            )

            # Update session info if not created
            if not created:
                user_session.last_activity = timezone.now()
                user_session.user_agent = self.get_user_agent(request)
                user_session.save(update_fields=["last_activity", "user_agent"])

            # Add geographic information if not already set
            if created or not user_session.country:
                self.add_geographic_info(user_session, request)

            # Check for suspicious activity
            self.check_suspicious_activity(user_session, request)

        except Session.DoesNotExist:
            # Session doesn't exist in database yet, skip
            pass
        except Exception as e:
            logger.error(f"Error in UserSessionTrackingMiddleware: {e}")

    def process_response(self, request, response):
        """Process response to update session information."""
        # Update last activity for authenticated users
        if (
            request.user.is_authenticated
            and hasattr(request, "session")
            and request.session.session_key
        ):

            try:
                session_obj = Session.objects.get(
                    session_key=request.session.session_key
                )
                UserSession.objects.filter(session=session_obj).update(
                    last_activity=timezone.now()
                )
            except (Session.DoesNotExist, UserSession.DoesNotExist):
                pass
            except Exception as e:
                logger.error(f"Error updating session activity: {e}")

    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
        return ip

    def get_user_agent(self, request):
        """Extract user agent from request."""
        return request.META.get("HTTP_USER_AGENT", "")[:1000]  # Limit length

    def get_login_method(self, request):
        """Determine login method from session/request."""
        # Check session for login method hints
        if hasattr(request, "session"):
            if request.session.get("social_auth_last_login_backend"):
                return "social"
            elif request.session.get("oauth_login"):
                return "oauth"
        return "password"  # Default

    def add_geographic_info(self, user_session, request):
        """Add geographic information using GeoIP2."""
        if not GEOIP2_AVAILABLE:
            logger.debug("GeoIP2 not available, skipping geographic info")
            return

        try:
            # Only try if we have a real IP (not localhost)
            ip = user_session.ip_address
            if ip and ip not in ["127.0.0.1", "localhost", "::1"]:
                g = GeoIP2()
                country = g.country(ip)
                city_info = g.city(ip)

                user_session.country = country.get("country_name", "")[:100]
                user_session.city = city_info.get("city", "")[:100]
                user_session.save(update_fields=["country", "city"])

        except Exception as e:
            # GeoIP2 might not be configured or IP might be invalid
            logger.debug(
                f"Could not get geographic info for IP {user_session.ip_address}: {e}"
            )

    def check_suspicious_activity(self, user_session, request):
        """Check for potentially suspicious login activity."""
        try:
            user = user_session.user
            current_ip = user_session.ip_address

            # Get recent sessions for this user (last 30 days)
            recent_sessions = UserSession.objects.filter(
                user=user, created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).exclude(id=user_session.id)

            # Check for suspicious patterns
            suspicious = False

            # 1. Login from new country
            if user_session.country:
                known_countries = recent_sessions.values_list(
                    "country", flat=True
                ).distinct()
                if user_session.country not in known_countries and known_countries:
                    suspicious = True
                    logger.warning(
                        f"New country login for user {user.email}: {user_session.country}"
                    )

            # 2. Multiple IPs in short time
            recent_ips = (
                recent_sessions.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(hours=1)
                )
                .values_list("ip_address", flat=True)
                .distinct()
            )

            if len(recent_ips) > 3:
                suspicious = True
                logger.warning(f"Multiple IPs for user {user.email} in last hour")

            # 3. Unusual user agent
            common_agents = recent_sessions.values_list("user_agent", flat=True)
            current_agent = user_session.user_agent

            # Simple check - if user agent is completely different from recent ones
            if common_agents and not any(
                agent[:50] in current_agent for agent in common_agents if agent
            ):
                suspicious = True
                logger.warning(f"Unusual user agent for user {user.email}")

            # Update suspicious flag
            if suspicious:
                user_session.is_suspicious = True
                user_session.save(update_fields=["is_suspicious"])

        except Exception as e:
            logger.error(f"Error checking suspicious activity: {e}")


class SessionCleanupMiddleware:
    """
    Middleware to clean up expired UserSession objects.
    Runs periodically to remove sessions that are no longer valid.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.cleanup_counter = 0

    def __call__(self, request):
        # Run cleanup every 100 requests to avoid performance impact
        self.cleanup_counter += 1
        if self.cleanup_counter >= 100:
            self.cleanup_expired_sessions()
            self.cleanup_counter = 0

        response = self.get_response(request)
        return response

    def cleanup_expired_sessions(self):
        """Remove UserSession objects for expired Django sessions."""
        try:
            # Get all expired session keys
            expired_session_keys = Session.objects.filter(
                expire_date__lt=timezone.now()
            ).values_list("session_key", flat=True)

            # Mark corresponding UserSessions as inactive
            UserSession.objects.filter(
                session__session_key__in=expired_session_keys, is_active=True
            ).update(is_active=False)

            logger.debug(f"Cleaned up {len(expired_session_keys)} expired sessions")

        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
