from http import HTTPStatus
from typing import TYPE_CHECKING

from django.urls import reverse_lazy

if TYPE_CHECKING:
    from django.test import Client


def test_admin_login_page_opens(client: Client) -> None:
    response = client.get(reverse_lazy("admin:login"))

    assert response.status_code == HTTPStatus.OK
