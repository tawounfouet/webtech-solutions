from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("sessions/", views.user_sessions, name="user_sessions"),
    path(
        "sessions/terminate/<int:session_id>/",
        views.terminate_session,
        name="terminate_session",
    ),
    path(
        "sessions/terminate-all/",
        views.terminate_all_sessions,
        name="terminate_all_sessions",
    ),
    path("security/", views.session_security_info, name="session_security_info"),
]
