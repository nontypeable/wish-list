from typing import TYPE_CHECKING

from django.http import HttpRequest

if TYPE_CHECKING:
    from users.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User
