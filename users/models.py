from typing import Any, ClassVar

from django.contrib.auth import password_validation
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, fields


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def create_user(
        self,
        email: str,
        password: str,
        username: str,
        first_name: str,
        last_name: str,
        **extra_fields: Any,
    ) -> User:
        if not email:
            raise ValidationError("Users must have an email")
        if not password:
            raise ValidationError("Users must have a password")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        password_validation.validate_password(password, user)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        username: str,
        first_name: str,
        last_name: str,
        **extra_fields: Any,
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        if not extra_fields.get("is_staff"):
            raise ValidationError("Superuser must have is_staff=True.")

        extra_fields.setdefault("is_superuser", True)
        if not extra_fields.get("is_superuser"):
            raise ValidationError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, username, first_name, last_name, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = fields.EmailField(verbose_name="Email", unique=True)
    username = fields.CharField(
        verbose_name="Username",
        max_length=255,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    first_name = fields.CharField(verbose_name="First Name", max_length=255)
    last_name = fields.CharField(verbose_name="Last Name", max_length=255)

    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)

    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)

    objects: ClassVar[UserManager] = UserManager()

    EMAIL_FIELD: ClassVar[str] = "email"

    USERNAME_FIELD: ClassVar[str] = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = ["username", "first_name", "last_name"]

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_first_name_not_empty", condition=~Q(first_name="")
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_last_name_not_empty", condition=~Q(last_name="")
            ),
        ]

    def __str__(self) -> str:
        return self.email
