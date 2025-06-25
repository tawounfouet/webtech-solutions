from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from unittest.mock import patch, MagicMock
from .models import UserSession
from .middleware import UserSessionTrackingMiddleware, GEOIP2_AVAILABLE

User = get_user_model()


class UserSessionTrackingMiddlewareTest(TestCase):
    """Test suite for UserSessionTrackingMiddleware."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.middleware = UserSessionTrackingMiddleware(lambda r: None)

    def test_get_client_ip_with_forwarded_for(self):
        """Test IP extraction with X-Forwarded-For header."""
        request = self.factory.get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = "192.168.1.1, 10.0.0.1"

        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, "192.168.1.1")

    def test_get_client_ip_without_forwarded_for(self):
        """Test IP extraction without X-Forwarded-For header."""
        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, "192.168.1.100")

    def test_get_user_agent(self):
        """Test user agent extraction."""
        request = self.factory.get("/")
        request.META["HTTP_USER_AGENT"] = "Mozilla/5.0 Test Browser"

        user_agent = self.middleware.get_user_agent(request)
        self.assertEqual(user_agent, "Mozilla/5.0 Test Browser")

    def test_get_login_method_default(self):
        """Test default login method detection."""
        request = self.factory.get("/")
        request.session = SessionStore()

        method = self.middleware.get_login_method(request)
        self.assertEqual(method, "password")

    def test_get_login_method_social(self):
        """Test social login method detection."""
        request = self.factory.get("/")
        request.session = SessionStore()
        request.session["social_auth_last_login_backend"] = "google-oauth2"

        method = self.middleware.get_login_method(request)
        self.assertEqual(method, "social")

    def test_process_request_unauthenticated_user(self):
        """Test that unauthenticated users are ignored."""
        request = self.factory.get("/")
        request.user = MagicMock()
        request.user.is_authenticated = False

        # Should not raise any exceptions
        self.middleware.process_request(request)

    def test_process_request_no_session(self):
        """Test request without session."""
        request = self.factory.get("/")
        request.user = self.user
        # No session attribute

        # Should not raise any exceptions
        self.middleware.process_request(request)

    @patch("authentication.middleware.GeoIP2")
    def test_add_geographic_info_success(self, mock_geoip):
        """Test successful geographic info addition."""
        if not GEOIP2_AVAILABLE:
            self.skipTest("GeoIP2 not available")

        # Mock GeoIP2 responses
        mock_geoip.return_value.country.return_value = {"country_name": "France"}
        mock_geoip.return_value.city.return_value = {"city": "Paris"}

        # Create a UserSession
        session = SessionStore()
        session.save()
        session_obj = Session.objects.create(
            session_key=session.session_key,
            session_data=session.encode({}),
            expire_date=session.get_expiry_date(),
        )

        user_session = UserSession.objects.create(
            user=self.user, session=session_obj, ip_address="8.8.8.8"
        )

        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = "8.8.8.8"

        self.middleware.add_geographic_info(user_session, request)

        user_session.refresh_from_db()
        self.assertEqual(user_session.country, "France")
        self.assertEqual(user_session.city, "Paris")

    @patch("authentication.middleware.GeoIP2")
    def test_add_geographic_info_failure(self, mock_geoip):
        """Test geographic info addition with GeoIP2 failure."""
        if not GEOIP2_AVAILABLE:
            self.skipTest("GeoIP2 not available")

        # Mock GeoIP2 to raise an exception
        mock_geoip.side_effect = Exception("GeoIP2 not configured")

        session = SessionStore()
        session.save()
        session_obj = Session.objects.create(
            session_key=session.session_key,
            session_data=session.encode({}),
            expire_date=session.get_expiry_date(),
        )

        user_session = UserSession.objects.create(
            user=self.user, session=session_obj, ip_address="8.8.8.8"
        )

        request = self.factory.get("/")

        # Should not raise exception
        self.middleware.add_geographic_info(user_session, request)

        user_session.refresh_from_db()
        self.assertEqual(user_session.country, "")
        self.assertEqual(user_session.city, "")

    def test_check_suspicious_activity_new_country(self):
        """Test suspicious activity detection for new country."""
        # Create existing session from France
        session1 = SessionStore()
        session1.save()
        session_obj1 = Session.objects.create(
            session_key=session1.session_key,
            session_data=session1.encode({}),
            expire_date=session1.get_expiry_date(),
        )

        UserSession.objects.create(
            user=self.user,
            session=session_obj1,
            ip_address="192.168.1.1",
            country="France",
        )

        # Create new session from different country with unique session key
        session2 = SessionStore()
        session2.save()
        session_obj2 = Session.objects.create(
            session_key=session2.session_key,
            session_data=session2.encode({}),
            expire_date=session2.get_expiry_date(),
        )

        user_session = UserSession.objects.create(
            user=self.user,
            session=session_obj2,
            ip_address="8.8.8.8",
            country="United States",
        )

        request = self.factory.get("/")

        self.middleware.check_suspicious_activity(user_session, request)

        user_session.refresh_from_db()
        self.assertTrue(user_session.is_suspicious)

    def tearDown(self):
        """Clean up test data."""
        try:
            UserSession.objects.all().delete()
            Session.objects.all().delete()
            User.objects.all().delete()
        except Exception:
            # Ignore cleanup errors in tests
            pass
