import hashlib
import secrets
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods, require_POST

from users.models import User
from wishes.models import AvailableWishList, WishList, WishListInvitation

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from django.http.response import HttpResponse

    class AuthenticatedHttpRequest(HttpRequest):
        user: User


def _generate_code(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


@login_required(login_url=reverse_lazy("users:sign_in"))
@require_POST
def create_invitation(request: AuthenticatedHttpRequest) -> HttpResponse:
    user = request.user
    wish_list = get_object_or_404(WishList, user=user)
    code = _generate_code()
    invention = WishListInvitation.objects.create(
        invited_email=request.POST["email"],
        wish_list=wish_list,
        code_hash=hashlib.sha256(code.encode("UTF-8")).hexdigest(),
    )
    invention.save()
    path = reverse(
        "wishes:accept_invitation",
        kwargs={"code": code},
    )
    invitation_url = request.build_absolute_uri(path)
    return render(
        request,
        "wishes/invitations/created.html",
        {
            "invitation_url": invitation_url,
            "recipient_email": invention.invited_email,
        },
    )


@login_required(login_url=reverse_lazy("users:sign_in"))
@require_http_methods(["GET", "POST"])
def accept_invitation(request: AuthenticatedHttpRequest, code: str) -> HttpResponse:
    user = request.user
    invite = get_object_or_404(
        WishListInvitation.objects.select_related("wish_list__user"),
        invited_email=user.email,
        code_hash=hashlib.sha256(code.encode("UTF-8")).hexdigest(),
    )
    access = AvailableWishList.objects.filter(wish_list=invite.wish_list, user=user)

    if request.method == "POST":
        with transaction.atomic():
            User.objects.select_for_update().get(pk=user.pk)
            if not access.exists():
                AvailableWishList.objects.create(wish_list=invite.wish_list, user=user)
        return redirect("wishes:shared_wishlists")

    owner = invite.wish_list.user
    return render(
        request,
        "wishes/invitations/accept.html",
        {
            "inviter_name": owner.first_name or owner.username,
            "recipient_email": invite.invited_email,
            "invitation_path": request.path,
            "has_access": access.exists(),
            "can_accept": True,
        },
    )


@login_required(login_url=reverse_lazy("users:sign_in"))
def get_accepted_wish_lists(request: AuthenticatedHttpRequest) -> HttpResponse:
    wish_lists = (
        WishList.objects.filter(accesses__user=request.user).select_related("user").distinct()
    )
    return render(
        request,
        "wishes/available_wish_lists.html",
        {"shared_wish_lists": wish_lists},
    )


@login_required(login_url=reverse_lazy("users:sign_in"))
def manage_access(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "GET":
        accesses = AvailableWishList.objects.filter(wish_list=request.user.wishlist)
        pending_accesses = WishListInvitation.objects.filter(wish_list=request.user.wishlist)
        return render(
            request,
            "wishes/invitations/manage.html",
            {"accesses": accesses, "pending_invitations": pending_accesses},
        )
    return render(request, "wishes/invitations/manage.html")
