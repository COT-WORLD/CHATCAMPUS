from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy


class CustomUserManager(BaseUserManager):

    """User manager wehere email is the unique identifier."""

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(gettext_lazy("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(gettext_lazy(
                "Superuser must have is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(gettext_lazy(
                "Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)
