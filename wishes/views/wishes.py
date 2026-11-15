from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from wishes.forms import CreateWishForm
from wishes.models import Wish, WishList

if TYPE_CHECKING:
    from django.http.request import HttpRequest

    from users.models import User

    class AuthenticatedHttpRequest(HttpRequest):
        user: User


@login_required(login_url=reverse_lazy("users:sign_in"))
def get_wish_list(request: AuthenticatedHttpRequest) -> HttpResponse:
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


@login_required(login_url=reverse_lazy("users:sign_in"))
def create_wish(request: AuthenticatedHttpRequest) -> HttpResponse:
    user = request.user
    if request.method == "POST":
        form = CreateWishForm(request.POST, request.FILES)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.wish_list = WishList.objects.get(user=user)
            wish.save()
            return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))
    else:
        form = CreateWishForm()
    return render(request, "wishes/create_wish.html", {"form": form})


@login_required(login_url=reverse_lazy("users:sign_in"))
@require_POST
def fulfill_wish(request: AuthenticatedHttpRequest, wish: int) -> HttpResponse:
    selected_wish = get_object_or_404(Wish, id=wish, wish_list__user=request.user)
    selected_wish.fulfilled = True
    selected_wish.save(update_fields=["fulfilled"])
    return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))
