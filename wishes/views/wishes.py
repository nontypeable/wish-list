from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View

from wishes.forms import CreateWishForm
from wishes.models import AvailableWishList, Wish, WishList

if TYPE_CHECKING:
    from django.http.request import HttpRequest

    from users.models import User

    class AuthenticatedHttpRequest(HttpRequest):
        user: User


class GetWishList(View):
    @login_required(login_url=reverse_lazy("users:sign_in"))
    async def get(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        wishes = Wish.objects.filter(wish_list__user=request.user)
        show_fulfilled = request.GET.get("status") == "fulfilled"
        return render(
            request,
            "wishes/wish_list.html",
            {
                "wishes": wishes.filter(fulfilled=show_fulfilled),
                "show_fulfilled": show_fulfilled,
                "active_count": wishes.filter(fulfilled=False).count(),
                "fulfilled_count": wishes.filter(fulfilled=True).count(),
            },
        )


class CreateWish(View):
    @login_required(login_url=reverse_lazy("users:sign_in"))
    async def get(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        form = CreateWishForm()
        return render(request, "wishes/create_wish.html", {"form": form})

    @login_required(login_url=reverse_lazy("users:sign_in"))
    async def post(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        user = request.user
        form = CreateWishForm(request.POST, request.FILES)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.wish_list = WishList.objects.get(user=user)
            wish.save()
            return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))
        return render(request, "wishes/create_wish.html", {"form": form})


class FulfillWish(View):
    @login_required(login_url=reverse_lazy("users:sign_in"))
    async def post(self, request: AuthenticatedHttpRequest, wish: int) -> HttpResponse:
        selected_wish = get_object_or_404(Wish, id=wish, wish_list__user=request.user)
        selected_wish.fulfilled = True
        selected_wish.save(update_fields=["fulfilled"])
        return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))


class OpenWish(View):
    @login_required(login_url=reverse_lazy("users:sign_in"))
    async def get(self, request: AuthenticatedHttpRequest, wish_list_id: int) -> HttpResponse:
        target_wish_list = get_object_or_404(WishList, pk=wish_list_id)
        have_access = (
            AvailableWishList.objects.filter(
                wish_list=target_wish_list, user_id=request.user.id
            ).exists()
            or target_wish_list.user == request.user
        )
        if not have_access:
            return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))
        status = request.GET.get("status") == "fulfilled"
        wishes = Wish.objects.filter(wish_list=target_wish_list, fulfilled=status)
        return render(
            request,
            "wishes/shared_wish_list.html",
            {
                "wish_list": target_wish_list,
                "wishes": wishes,
                "show_fulfilled": status,
                "active_count": Wish.objects.filter(
                    wish_list=target_wish_list, fulfilled=False
                ).count(),
                "fulfilled_count": Wish.objects.filter(
                    wish_list=target_wish_list, fulfilled=True
                ).count(),
            },
        )
