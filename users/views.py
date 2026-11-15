from typing import TYPE_CHECKING

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from users.forms import UserSignInForm, UserSignUpForm

if TYPE_CHECKING:
    from django.http.request import HttpRequest


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    return render(request, "users/profile.html", {"user": request.user})


def sign_up(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:profile"))

    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("users:profile"))
    else:
        form = UserSignUpForm()
    return render(request, "users/sign_up.html", {"form": form})


def sign_in(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:profile"))

    if request.method == "POST":
        form = UserSignInForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["email"], password=form.cleaned_data["password"]
            )
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse("users:profile"))
            form.add_error(None, "Неверная электронная почта или пароль.")
    else:
        form = UserSignInForm()
    return render(request, "users/sign_in.html", {"form": form})
