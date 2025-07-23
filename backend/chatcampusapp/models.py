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


# Topic model
class Topic(models.Model):
    topic_name = models.CharField(gettext_lazy(
        "topic name"), max_length=150, blank=False, null=False, unique=True)
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["topic_name"])
        ]

    def __str__(self):
        return self.topic_name


# Room model
class Room(models.Model):
    room_name = models.CharField(gettext_lazy(
        "room name"), max_length=200, null=False, blank=False)
    room_description = models.TextField(gettext_lazy(
        "room description"), null=False, blank=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name="room_owner")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL,
                              null=True, blank=False, related_name="room_topic")
    participants = models.ManyToManyField(
        User, related_name="room_participants")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["topic"]),
            models.Index(fields=["room_name"]),
            models.Index(fields=["room_description"]),
        ]

    def __str__(self):
        return self.room_name
