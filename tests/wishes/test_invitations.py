import hashlib
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test import Client
from django.urls import reverse

from users.models import User
from wishes.models import AvailableWishList, WishList, WishListInvitation

if TYPE_CHECKING:
    from django.http import HttpResponse


@pytest.fixture
def invitation(db: None) -> tuple[User, WishListInvitation, str]:
    owner = User.objects.create(
        email="owner@example.com", username="owner", first_name="Андрей", last_name="Иванов"
    )
    recipient = User.objects.create(
        email="friend@example.com", username="friend", first_name="Мария", last_name="Петрова"
    )
    wish_list = WishList.objects.create(user=owner, name="Желания Андрея")
    code = "invitation-code-for-test"
    invite = WishListInvitation.objects.create(
        wish_list=wish_list,
        invited_email=recipient.email,
        code_hash=hashlib.sha256(code.encode()).hexdigest(),
    )
    return recipient, invite, code


def test_opening_invitation_does_not_grant_access(
    client: Client, invitation: tuple[User, WishListInvitation, str]
) -> None:
    recipient, _, code = invitation
    client.force_login(recipient)

    response = client.get(reverse("wishes:accept_invitation", kwargs={"code": code}))

    assert response.status_code == HTTPStatus.OK
    assert "Принять приглашение" in response.content.decode()
    assert not AvailableWishList.objects.exists()


def test_accept_invitation_redirects_to_accessible_wish_lists(
    client: Client, invitation: tuple[User, WishListInvitation, str]
) -> None:
    recipient, invite, code = invitation
    client.force_login(recipient)

    response = client.post(reverse("wishes:accept_invitation", kwargs={"code": code}))

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("wishes:shared_wishlists")
    assert AvailableWishList.objects.filter(user=recipient, wish_list=invite.wish_list).exists()
    listing = client.get(response.url)
    assert list(listing.context["shared_wish_lists"]) == [invite.wish_list]
    assert invite.wish_list.user.first_name in listing.content.decode()


def test_accept_invitation_twice_does_not_duplicate_access(
    client: Client, invitation: tuple[User, WishListInvitation, str]
) -> None:
    recipient, invite, code = invitation
    client.force_login(recipient)
    url = reverse("wishes:accept_invitation", kwargs={"code": code})

    client.post(url)
    response = client.post(url)

    assert response.status_code == HTTPStatus.FOUND
    assert AvailableWishList.objects.filter(user=recipient, wish_list=invite.wish_list).count() == 1


def test_existing_duplicate_accesses_do_not_break_acceptance_or_listing(
    client: Client, invitation: tuple[User, WishListInvitation, str]
) -> None:
    recipient, invite, code = invitation
    for _ in range(2):
        AvailableWishList.objects.create(user=recipient, wish_list=invite.wish_list)
    client.force_login(recipient)

    response = client.post(reverse("wishes:accept_invitation", kwargs={"code": code}))

    assert response.status_code == HTTPStatus.FOUND
    assert AvailableWishList.objects.filter(user=recipient, wish_list=invite.wish_list).count() == 2
    listing = client.get(reverse("wishes:shared_wishlists"))
    assert list(listing.context["shared_wish_lists"]) == [invite.wish_list]


@pytest.mark.parametrize("method", ["get", "post"])
def test_invitation_for_another_email_returns_404(
    client: Client, invitation: tuple[User, WishListInvitation, str], method: str
) -> None:
    _, invite, code = invitation
    client.force_login(invite.wish_list.user)

    response: HttpResponse = getattr(client, method)(
        reverse("wishes:accept_invitation", kwargs={"code": code})
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not AvailableWishList.objects.exists()


@pytest.mark.parametrize("method", ["get", "post"])
def test_unknown_invitation_returns_404(
    client: Client, invitation: tuple[User, WishListInvitation, str], method: str
) -> None:
    recipient, _, _ = invitation
    client.force_login(recipient)

    response: HttpResponse = getattr(client, method)(
        reverse("wishes:accept_invitation", kwargs={"code": "unknown"})
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not AvailableWishList.objects.exists()


def test_accepting_invitation_requires_csrf(
    invitation: tuple[User, WishListInvitation, str],
) -> None:
    recipient, _, code = invitation
    client = Client(enforce_csrf_checks=True)
    client.force_login(recipient)

    response = client.post(reverse("wishes:accept_invitation", kwargs={"code": code}))

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert not AvailableWishList.objects.exists()
