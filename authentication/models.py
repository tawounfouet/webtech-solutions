from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """
    Custom manager for User model with email as the unique identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model using email as the unique identifier instead of username.
    Follows Django best practices by extending AbstractUser.
    """

    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        help_text="Required. Enter a valid email address.",
    )
    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        null=True,
        verbose_name="Username",
        help_text="Optional. Username for display purposes.",
    )

    # Additional fields for better user management
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name="Email Verified",
        help_text="Designates whether this user has verified their email address.",
    )

    # Use our custom manager
    objects = UserManager()

    # Use email as the unique identifier for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "auth_user"

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name


class UserProfile(models.Model):
    """
    Extended user profile information.
    Separate model to keep the User model lean and allow for future extensions.
    """

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female")
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="User"
    )

    # Personal Information
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Biography",
        help_text="Tell us about yourself.",
    )
    birth_date = models.DateField(blank=True, null=True, verbose_name="Birth Date")
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="Gender"
    )

    # Contact Information
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, verbose_name="Phone Number"
    )

    # Address Information
    address = models.CharField(max_length=255, blank=True, verbose_name="Address")
    city = models.CharField(max_length=100, blank=True, verbose_name="City")
    country = models.CharField(max_length=100, blank=True, verbose_name="Country")
    postal_code = models.CharField(
        max_length=20, blank=True, verbose_name="Postal Code"
    )

    # Profile Settings
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Avatar"
    )
    timezone = models.CharField(max_length=50, default="UTC", verbose_name="Timezone")
    language = models.CharField(
        max_length=10, default="en", verbose_name="Preferred Language"
    )

    # Privacy Settings
    is_profile_public = models.BooleanField(
        default=False,
        verbose_name="Public Profile",
        help_text="Make profile visible to other users.",
    )
    receive_notifications = models.BooleanField(
        default=True,
        verbose_name="Receive Notifications",
        help_text="Receive email notifications.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        db_table = "auth_user_profile"

    def __str__(self):
        return f"{self.user.email}'s Profile"

    def get_age(self):
        """Calculate and return the user's age."""
        if self.birth_date:
            today = timezone.now().date()
            return (
                today.year
                - self.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.birth_date.month, self.birth_date.day)
                )
            )
        return None


class UserSession(models.Model):
    """
    Track user sessions for security and monitoring purposes.
    Extends Django's built-in session system with additional user information.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_sessions",
        verbose_name="User",
    )
    session = models.OneToOneField(
        Session,
        on_delete=models.CASCADE,
        related_name="user_session_info",
        verbose_name="Django Session",
    )

    # Session Information
    ip_address = models.GenericIPAddressField(
        verbose_name="IP Address",
        help_text="IP address from which the session was created.",
    )
    user_agent = models.TextField(
        blank=True, verbose_name="User Agent", help_text="Browser/client information."
    )

    # Geographic Information (optional)
    country = models.CharField(max_length=100, blank=True, verbose_name="Country")
    city = models.CharField(max_length=100, blank=True, verbose_name="City")

    # Session Tracking
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Session Created")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Last Activity")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    # Security Flags
    is_suspicious = models.BooleanField(
        default=False,
        verbose_name="Suspicious Activity",
        help_text="Flag for potentially suspicious login activity.",
    )
    login_method = models.CharField(
        max_length=50,
        default="password",
        verbose_name="Login Method",
        help_text="Method used for authentication (password, social, etc.)",
    )

    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        db_table = "auth_user_session"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["ip_address"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.ip_address} ({self.created_at})"

    def get_session_duration(self):
        """Calculate session duration."""
        return self.last_activity - self.created_at

    def is_expired(self):
        """Check if session is expired based on Django session expiry."""
        return self.session.expire_date < timezone.now()

    def terminate_session(self):
        """Terminate the session and mark as inactive."""
        self.is_active = False
        self.save()
        # Delete the Django session
        self.session.delete()


# Signal handlers to automatically create/update profiles
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()
