from typing import TYPE_CHECKING

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .forms import AdminUserChangeForm, UserSignUpForm
from .models import User

if TYPE_CHECKING:
    BaseUserAdmin = DjangoUserAdmin[User]
else:
    BaseUserAdmin = DjangoUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = AdminUserChangeForm
    add_form = UserSignUpForm
    list_display = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_active")

    list_display_links = ("id", "username", "email")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at", "last_login")
    fieldsets = (
        ("Пользователь", {"fields": ("first_name", "last_name", "username", "email", "password")}),
        (
            "Права",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (
            "Даты",
            {
                "fields": ("created_at", "updated_at", "last_login"),
            },
        ),
    )
    add_fieldsets = (
        (
            "Новый пользователь",
            {
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
