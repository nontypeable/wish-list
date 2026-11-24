import hashlib
import secrets
from typing import TYPE_CHECKING, Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from users.models import User
from wishes.forms import CreateInvitationForm
from wishes.models import AvailableWishList, WishList, WishListInvitation

if TYPE_CHECKING:
    from django.http.response import HttpResponse

    from wishes.views._types import AuthenticatedHttpRequest

    BaseInvitationCreateView = CreateView[WishListInvitation, CreateInvitationForm]
else:
    BaseInvitationCreateView = CreateView


def _generate_code(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


class InvitationCreateView(LoginRequiredMixin, BaseInvitationCreateView):
    request: AuthenticatedHttpRequest

    model = WishListInvitation
    form_class = CreateInvitationForm
    login_url = reverse_lazy("users:sign_in")
    template_name = "wishes/invitations/create.html"

    def form_valid(self, form: CreateInvitationForm) -> HttpResponse:
        code = _generate_code()
        form.instance.wish_list = WishList.objects.get(user=self.request.user)
        form.instance.code_hash = hashlib.sha256(code.encode("UTF-8")).hexdigest()
        self.object = form.save()
        path = reverse(
            "wishes:accept_invitation",
            kwargs={"code": code},
        )
        invitation_url = self.request.build_absolute_uri(path)
        return render(
            self.request,
            "wishes/invitations/created.html",
            {
                "invitation_url": invitation_url,
                "recipient_email": self.object.invited_email,
            },
        )


class InvitationAcceptView(LoginRequiredMixin, TemplateView):
    request: AuthenticatedHttpRequest

    login_url = reverse_lazy("users:sign_in")
    template_name = "wishes/invitations/accept.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        invite = WishListInvitation.objects.get(
            invited_email=self.request.user.email,
            code_hash=hashlib.sha256(kwargs["code"].encode("UTF-8")).hexdigest(),
        )
        access = AvailableWishList.objects.filter(
            wish_list=invite.wish_list, user=self.request.user
        )

        context["inviter_name"] = invite.wish_list.user.first_name or invite.wish_list.user.username
        context["recipient_email"] = invite.invited_email
        context["invitation_path"] = self.request.path
        context["has_access"] = access.exists()
        context["can_accept"] = True

        return context

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
