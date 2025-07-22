from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from .managers import CustomUserManager
from django.utils.translation import gettext_lazy

# Custom User model with AbstractUser, PermissionsMixin and CustomUserManager


class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(gettext_lazy(
        "email address"), unique=True, null=False, blank=False)
    first_name = models.CharField(gettext_lazy(
        "first name"), max_length=150, null=True, blank=True)
    last_name = models.CharField(gettext_lazy(
        "last name"), max_length=150, null=True, blank=True)
    bio = models.TextField(gettext_lazy("bio"), null=True, blank=True)
    avatar = models.FileField(gettext_lazy(
        "avatar"), upload_to="images/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
