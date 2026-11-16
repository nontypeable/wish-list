from http import HTTPStatus
from io import BytesIO
from typing import TYPE_CHECKING

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse_lazy
from PIL import Image

from users.models import User
from wishes.models import Wish, WishList

if TYPE_CHECKING:
    from pathlib import Path

    from django.test import Client
    from pytest_django.fixtures import SettingsWrapper

PASSWORD = "Kx7#mQ2!vLp9"  # noqa: S105 — тестовое значение


@pytest.fixture
def owner(db: None) -> User:
    return User.objects.create_user("owner@example.com", PASSWORD, "owner", "Олег", "Орлов")


def test_wish_list_shows_own_wishes(client: Client, owner: User) -> None:
    wish_list = WishList.objects.create(user=owner, name="Мои желания")
    Wish.objects.create(name="Книга", price=500, wish_list=wish_list)
    client.force_login(owner)

    response = client.get(reverse_lazy("wishes:get_wish_list"))

    content = response.content.decode()
    assert response.status_code == HTTPStatus.OK
    assert "Книга" in content
    assert "500" in content


@override_settings(MEDIA_URL="/media/")
def test_wish_list_shows_wish_image(client: Client, owner: User) -> None:
    wish_list = WishList.objects.create(user=owner, name="Мои желания")
    Wish.objects.create(name="Книга", image="wishes/book.png", wish_list=wish_list)
    client.force_login(owner)

    response = client.get(reverse_lazy("wishes:get_wish_list"))

    assert 'src="/media/wishes/book.png"' in response.content.decode()


def test_wish_list_does_not_show_other_users_wishes(client: Client, owner: User) -> None:
    other = User.objects.create_user("other@example.com", PASSWORD, "other", "Пётр", "Сидоров")
    other_list = WishList.objects.create(user=other, name="Чужой")
    Wish.objects.create(name="Чужое желание", wish_list=other_list)
    client.force_login(owner)

    response = client.get(reverse_lazy("wishes:get_wish_list"))

    assert "Чужое желание" not in response.content.decode()


def test_wish_list_shows_empty_state(client: Client, owner: User) -> None:
    client.force_login(owner)

    response = client.get(reverse_lazy("wishes:get_wish_list"))

    assert "В списке пока ничего нет." in response.content.decode()


def test_wish_list_filters_fulfilled_wishes(client: Client, owner: User) -> None:
    wish_list = WishList.objects.create(user=owner, name="Мои желания")
    planned = Wish.objects.create(name="Фотоаппарат", wish_list=wish_list)
    fulfilled = Wish.objects.create(name="Книга", wish_list=wish_list, fulfilled=True)
    other = User.objects.create_user("other@example.com", PASSWORD, "other", "Пётр", "Сидоров")
    other_list = WishList.objects.create(user=other, name="Чужой")
    Wish.objects.create(name="Чужое желание", wish_list=other_list, fulfilled=True)
    client.force_login(owner)

    response = client.get(reverse_lazy("wishes:get_wish_list"), {"status": "fulfilled"})

    assert list(response.context["wishes"]) == [fulfilled]
    assert response.context["active_count"] == 1
    assert response.context["fulfilled_count"] == 1
    assert "Чужое желание" not in response.content.decode()

    response = client.get(reverse_lazy("wishes:get_wish_list"))

    assert list(response.context["wishes"]) == [planned]


def test_fulfilled_wishes_empty_state(client: Client, owner: User) -> None:
    WishList.objects.create(user=owner, name="Мои желания")
    client.force_login(owner)

    response = client.get(reverse_lazy("wishes:get_wish_list"), {"status": "fulfilled"})

    assert "Пока нет исполненных желаний." in response.content.decode()


def test_owner_can_fulfill_wish(client: Client, owner: User) -> None:
    wish_list = WishList.objects.create(user=owner, name="Мои желания")
    wish = Wish.objects.create(name="Книга", wish_list=wish_list)
    client.force_login(owner)

    response = client.post(reverse_lazy("wishes:fulfill_wish", args=[wish.pk]))

    wish.refresh_from_db()
    assert wish.fulfilled
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse_lazy("wishes:get_wish_list")
    assert not client.get(reverse_lazy("wishes:get_wish_list")).context["wishes"]
    assert list(
        client.get(reverse_lazy("wishes:get_wish_list"), {"status": "fulfilled"}).context["wishes"]
    ) == [wish]
    assert (
        client.post(reverse_lazy("wishes:fulfill_wish", args=[wish.pk])).status_code
        == HTTPStatus.FOUND
    )


def test_fulfilling_wish_requires_post(client: Client, owner: User) -> None:
    wish_list = WishList.objects.create(user=owner, name="Мои желания")
    wish = Wish.objects.create(name="Книга", wish_list=wish_list)
    client.force_login(owner)

    response = client.get(reverse_lazy("wishes:fulfill_wish", args=[wish.pk]))

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    wish.refresh_from_db()
    assert not wish.fulfilled


def test_cannot_fulfill_another_users_wish(client: Client, owner: User) -> None:
    other = User.objects.create_user("other@example.com", PASSWORD, "other", "Пётр", "Сидоров")
    wish_list = WishList.objects.create(user=other, name="Чужой")
    wish = Wish.objects.create(name="Чужое желание", wish_list=wish_list)
    client.force_login(owner)

    response = client.post(reverse_lazy("wishes:fulfill_wish", args=[wish.pk]))

    assert response.status_code == HTTPStatus.NOT_FOUND
    wish.refresh_from_db()
    assert not wish.fulfilled


def test_fulfilling_missing_wish_returns_404(client: Client, owner: User) -> None:
    client.force_login(owner)

    response = client.post(reverse_lazy("wishes:fulfill_wish", args=[999]))

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_wish_page_renders(client: Client, owner: User) -> None:
    client.force_login(owner)

    response = client.get(reverse_lazy("wishes:create_wish"))

    template_names = [t.name for t in response.templates]
    assert response.status_code == HTTPStatus.OK
    assert "wishes/create_wish.html" in template_names
    assert "base.html" in template_names


def test_create_wish_saves_uploaded_image(
    client: Client, owner: User, settings: SettingsWrapper, tmp_path: Path
) -> None:
    settings.MEDIA_ROOT = tmp_path
    WishList.objects.create(user=owner, name="Мои желания")
    client.force_login(owner)
    image_data = BytesIO()
    Image.new("RGB", (2, 2)).save(image_data, format="PNG")
    uploaded_image = SimpleUploadedFile("wish.png", image_data.getvalue(), "image/png")

    response = client.post(
        reverse_lazy("wishes:create_wish"),
        {"name": "Книга", "image": uploaded_image},
    )

    assert response.status_code == HTTPStatus.FOUND
    wish = Wish.objects.get(name="Книга", wish_list__user=owner)
    assert wish.image
    with wish.image.open("rb") as saved_image:
        assert saved_image.read() == image_data.getvalue()
