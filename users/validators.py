from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


class NoWhitespacePasswordValidator:
    """Запрещает пробелы, табы и прочие пробельные символы в пароле."""

    message = "Пароль не должен содержать пробелы."

    def validate(self, password: str, user: AbstractBaseUser | None = None) -> None:
        if any(char.isspace() for char in password):
            raise ValidationError(self.message, code="password_has_whitespace")

    def get_help_text(self) -> str:
        return self.message
