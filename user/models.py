import pathlib
import uuid

from django.contrib.auth.models import (
    AbstractUser,
    UserManager as DjangoUserManager
)
from django.db import models


def upload_to(instance, filename):
    user_name = instance.nickname

    filename = (
        f"{user_name}{uuid.uuid4()}{pathlib.Path(filename).suffix}"
    )

    return pathlib.Path(f"uploads/{user_name}/") / filename


class UserManager(DjangoUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    nickname = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    profile_pic = models.ImageField(
        upload_to=upload_to,
        null=True,
        blank=True,
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
