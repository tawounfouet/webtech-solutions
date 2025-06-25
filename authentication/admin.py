from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "username")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_email_verified",
        "date_joined",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "is_email_verified",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""

    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = (
        ("bio",),
        ("birth_date", "gender"),
        ("phone_number",),
        ("address", "city"),
        ("country", "postal_code"),
        ("avatar",),
        ("timezone", "language"),
        ("is_profile_public", "receive_notifications"),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model."""

    list_display = (
        "user",
        "phone_number",
        "city",
        "country",
        "is_profile_public",
        "created_at",
    )
    list_filter = (
        "gender",
        "country",
        "is_profile_public",
        "receive_notifications",
        "created_at",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone_number",
        "city",
    )
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (
            _("Personal Information"),
            {"fields": ("bio", "birth_date", "gender", "avatar")},
        ),
        (
            _("Contact Information"),
            {"fields": ("phone_number", "address", "city", "country", "postal_code")},
        ),
        (
            _("Preferences"),
            {
                "fields": (
                    "timezone",
                    "language",
                    "is_profile_public",
                    "receive_notifications",
                )
            },
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin for UserSession model."""

    list_display = (
        "user",
        "ip_address",
        "country",
        "city",
        "is_active",
        "is_suspicious",
        "created_at",
    )
    list_filter = (
        "is_active",
        "is_suspicious",
        "login_method",
        "country",
        "created_at",
    )
    search_fields = ("user__email", "ip_address", "user_agent")
    readonly_fields = ("created_at", "last_activity", "session")
    date_hierarchy = "created_at"

    fieldsets = (
        (_("User Information"), {"fields": ("user", "session")}),
        (
            _("Session Details"),
            {"fields": ("ip_address", "user_agent", "login_method")},
        ),
        (_("Location"), {"fields": ("country", "city")}),
        (_("Status"), {"fields": ("is_active", "is_suspicious")}),
        (_("Timestamps"), {"fields": ("created_at", "last_activity")}),
    )

    actions = ["terminate_sessions", "mark_as_suspicious"]

    def get_queryset(self, request):
        """
        Retourne toutes les sessions pour les superutilisateurs,
        sinon seulement les sessions de l'utilisateur connecté.
        """
        qs = super().get_queryset(request)

        # Debug info
        print(f"DEBUG: User {request.user.email} accessing UserSession admin")
        print(f"DEBUG: is_superuser: {request.user.is_superuser}")
        print(f"DEBUG: Total sessions in DB: {qs.count()}")

        # Les superutilisateurs et staff voient toutes les sessions
        if request.user.is_superuser or request.user.is_staff:
            print(f"DEBUG: Returning all sessions for admin user")
            return qs

        # Les autres utilisateurs ne voient que leurs propres sessions
        filtered_qs = qs.filter(user=request.user)
        print(f"DEBUG: Returning {filtered_qs.count()} sessions for regular user")
        return filtered_qs

    def has_change_permission(self, request, obj=None):
        """
        Permet aux superutilisateurs de modifier toutes les sessions,
        aux autres utilisateurs seulement leurs propres sessions.
        """
        if request.user.is_superuser:
            return True

        if obj and obj.user != request.user:
            return False

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Permet aux superutilisateurs de supprimer toutes les sessions,
        aux autres utilisateurs seulement leurs propres sessions.
        """
        if request.user.is_superuser:
            return True

        if obj and obj.user != request.user:
            return False

        return super().has_delete_permission(request, obj)

    def terminate_sessions(self, request, queryset):
        """Admin action to terminate selected sessions."""
        count = 0
        for session in queryset:
            if session.is_active:
                session.terminate_session()
                count += 1
        self.message_user(request, f"{count} sessions have been terminated.")

    terminate_sessions.short_description = "Terminate selected sessions"

    def mark_as_suspicious(self, request, queryset):
        """Admin action to mark sessions as suspicious."""
        count = queryset.update(is_suspicious=True)
        self.message_user(request, f"{count} sessions have been marked as suspicious.")

    mark_as_suspicious.short_description = "Mark as suspicious"


# Add UserProfile inline to User admin
UserAdmin.inlines = (UserProfileInline,)
