from typing import TYPE_CHECKING, Any, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View

from wishes.models import AvailableWishList, WishListInvitation

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from django.http.response import HttpResponse

    from wishes.views._types import AuthenticatedHttpRequest


class WishListAccessView(LoginRequiredMixin, View):
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
