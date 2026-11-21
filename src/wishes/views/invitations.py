import hashlib
import secrets
from typing import TYPE_CHECKING, Any, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View

from users.models import User
from wishes.forms import CreateInvitationForm
from wishes.models import AvailableWishList, WishList, WishListInvitation

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from django.http.response import HttpResponse

    class AuthenticatedHttpRequest(HttpRequest):
        user: User


def _generate_code(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


class CreateInvitation(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def post(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        form = CreateInvitationForm(request.POST)
        if form.is_valid():
            user = request.user
            email = form.cleaned_data["invited_email"]
            wish_list = get_object_or_404(WishList, user=user)

            code = _generate_code()
            invention = WishListInvitation.objects.create(
                invited_email=email,
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
        return render(request, "wishes/invitations/create.html", {"form": form})

    def get(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        form = CreateInvitationForm()
        return render(request, "wishes/invitations/create.html", {"form": form})


class AcceptInvitation(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")
    http_method_names = ("get", "post")

    def get(self, request: AuthenticatedHttpRequest, code: str) -> HttpResponse:
        user = request.user
        invite = get_object_or_404(
            WishListInvitation.objects.select_related("wish_list__user"),
            invited_email=user.email,
            code_hash=hashlib.sha256(code.encode("UTF-8")).hexdigest(),
        )
        access = AvailableWishList.objects.filter(wish_list=invite.wish_list, user=user)

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

    def post(self, request: AuthenticatedHttpRequest, code: str) -> HttpResponse:
        user = request.user
        invite = get_object_or_404(
            WishListInvitation.objects.select_related("wish_list__user"),
            invited_email=user.email,
            code_hash=hashlib.sha256(code.encode("UTF-8")).hexdigest(),
        )
        access = AvailableWishList.objects.filter(wish_list=invite.wish_list, user=user)

        with transaction.atomic():
            User.objects.select_for_update().get(pk=user.pk)
            if not access.exists():
                AvailableWishList.objects.create(wish_list=invite.wish_list, user=user)
                invite.accepted_at = timezone.now()
                invite.save(update_fields=["accepted_at"])
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


class GetAcceptedWishLists(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def get(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        wish_lists = (
            WishList.objects.filter(accesses__user=request.user).select_related("user").distinct()
        )
        return render(
            request,
            "wishes/available_wish_lists.html",
            {"shared_wish_lists": wish_lists},
        )

    post = get
    put = get
    patch = get
    delete = get
    trace = get

    def options(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.get(cast("AuthenticatedHttpRequest", request))


class ManageAccess(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def get(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        accesses = AvailableWishList.objects.filter(wish_list=request.user.wishlist)
        pending_accesses = WishListInvitation.objects.filter(
            wish_list=request.user.wishlist, accepted_at__isnull=True
        )
        return render(
            request,
            "wishes/invitations/manage.html",
            {"accesses": accesses, "pending_invitations": pending_accesses},
        )

    def post(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        return render(request, "wishes/invitations/manage.html")

    head = post
    put = post
    patch = post
    delete = post
    trace = post

    def options(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.post(cast("AuthenticatedHttpRequest", request))
