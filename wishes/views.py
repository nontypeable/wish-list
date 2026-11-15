from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from wishes.forms import CreateWishForm
from wishes.models import Wish, WishList

if TYPE_CHECKING:
    from django.http.request import HttpRequest


@login_required(login_url=reverse_lazy("users:login"))
def get_wish_list(request: HttpRequest) -> HttpResponse:
    user = request.user
    wish_list = WishList.objects.get(user=user)
    wishes = Wish.objects.all().filter(wish_list=wish_list.id)
    return render(request, "wishes/wish_list.html", {"wishes": wishes})


@login_required(login_url=reverse_lazy("users:login"))
def create_wish(request: HttpRequest) -> HttpResponse:
    user = request.user
    if request.method == "POST":
        form = CreateWishForm(request.POST, request.FILES)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = user
            wish.wish_list = WishList.objects.get(user=user)
            wish.save()
            return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))
    else:
        form = CreateWishForm()
    return render(request, "wishes/create_wish.html", {"form": form})
