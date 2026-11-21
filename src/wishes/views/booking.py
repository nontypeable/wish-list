from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View

from wishes.models import AvailableWishList, Wish

if TYPE_CHECKING:
    from wishes.views._types import AuthenticatedHttpRequest


class WishBookView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def post(self, request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
        try:
            wish = Wish.objects.get(id=pk)
            if not AvailableWishList.objects.filter(
                user=request.user, wish_list_id=wish.wish_list_id
            ).exists():
                return HttpResponse(status=403)
            wish.book(request.user)
        except Wish.DoesNotExist:
            return HttpResponse(status=404)
        except ValidationError as exc:
            return HttpResponse(" ".join(exc.messages), status=400)

        return redirect("wishes:open_other_wish_list", wish_list_id=wish.wish_list_id)


class WishUnbookView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def post(self, request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
        try:
            wish = Wish.objects.get(id=pk)
            if not AvailableWishList.objects.filter(
                user=request.user, wish_list_id=wish.wish_list_id
            ).exists():
                return HttpResponse(status=403)
            wish.unbook(request.user)
        except Wish.DoesNotExist:
            return HttpResponse(status=404)
        except ValidationError as exc:
            return HttpResponse(" ".join(exc.messages), status=400)
        return redirect("wishes:open_other_wish_list", wish_list_id=wish.wish_list_id)
