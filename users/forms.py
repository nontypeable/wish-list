from typing import ClassVar

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class UserSignUpForm(UserCreationForm[User]):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields: ClassVar[tuple[str, ...]] = ("first_name", "last_name", "username", "email")
        labels: ClassVar[dict[str, str]] = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "username": "Имя пользователя",
            "email": "Электронная почта",
        }


class UserSignInForm(forms.Form):
    email = forms.EmailField(label="Электронная почта")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput, strip=False)


class AdminUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
