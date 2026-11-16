from typing import TYPE_CHECKING

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from users.forms import UserSignInForm, UserSignUpForm
from wishes.models import WishList

if TYPE_CHECKING:
    from django.http.request import HttpRequest


def _redirect_after_auth(request: HttpRequest) -> HttpResponse:
    target = request.GET.get("next") or request.POST.get("next")
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(target)
    return redirect("users:profile")


class UserProfile(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "users/profile.html", {"user": request.user})


class UserSignUp(View):
    async def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("users:profile"))

        form = UserSignUpForm()
        return render(request, "users/sign_up.html", {"form": form})

    async def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("users:profile"))

        form = UserSignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                WishList.objects.create(user=user, name="Мои желания")
            login(request, user)
            return _redirect_after_auth(request)
        return render(request, "users/sign_up.html", {"form": form})


class UserSignIn(View):
    async def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("users:profile"))

        form = UserSignInForm()
        return render(request, "users/sign_in.html", {"form": form})

    async def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("users:profile"))

        form = UserSignInForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["email"], password=form.cleaned_data["password"]
            )
            if user:
                login(request, user)
                return _redirect_after_auth(request)
            form.add_error(None, "Неверная электронная почта или пароль.")
        return render(request, "users/sign_in.html", {"form": form})
