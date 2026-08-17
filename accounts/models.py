from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom PHARVO user.

    The `accounts_user` table already exists in the PostgreSQL database with an
    additional `role` column. `AUTH_USER_MODEL` is set to "accounts.User" in
    the project settings so Django uses this model instead of the built-in
    `auth.User` (which has no `auth_user` table in this database).
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        PHARMACIST = "pharmacist", "Pharmacist"
        ASSISTANT = "assistant", "Assistant"
        STAFF = "staff", "Staff"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PHARMACIST,
        verbose_name="role",
    )

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username
