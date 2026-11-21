from typing import TYPE_CHECKING, Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from wishes.forms import CreateWishForm
from wishes.models import AvailableWishList, Wish, WishList

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http.request import HttpRequest

    from users.models import User

    class AuthenticatedHttpRequest(HttpRequest):
        user: User


class GetWishList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:sign_in")
    context_object_name = "wishes"
    template_name = "wishes/wish_list.html"

    def get_queryset(self) -> QuerySet[Wish]:
        show_fulfilled = self.request.GET.get("status") == "fulfilled"
        return Wish.objects.filter(
            wish_list__user=self.request.user,
            fulfilled=show_fulfilled,
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        all_wishes = Wish.objects.filter(
            wish_list__user=self.request.user,
        )

        context["show_fulfilled"] = self.request.GET.get("status") == "fulfilled"
        context["active_count"] = all_wishes.filter(fulfilled=False).count()
        context["fulfilled_count"] = all_wishes.filter(fulfilled=True).count()

        return context


class CreateWish(LoginRequiredMixin, CreateView):
    model = Wish
    form_class = CreateWishForm
    login_url = reverse_lazy("users:sign_in")
    template_name = "wishes/create_wish.html"
    success_url = reverse_lazy("wishes:get_wish_list")

    def form_valid(self, form: CreateWishForm) -> HttpResponse:
        form.instance.wish_list = WishList.objects.get(user=form.instance.user)
        return super().form_valid(form)


class FulfillWish(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def post(self, request: AuthenticatedHttpRequest, wish: int) -> HttpResponse:
        selected_wish = get_object_or_404(Wish, id=wish, wish_list__user=request.user)
        selected_wish.fulfilled = True
        selected_wish.save(update_fields=["fulfilled"])
        return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))


class BookWish(LoginRequiredMixin, View):
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


class UnBookWish(LoginRequiredMixin, View):
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


class OpenWish(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:sign_in")
    model = Wish
    context_object_name = "wishes"
    template_name = "wishes/shared_wish_list.html"

    def get_queryset(self) -> QuerySet[Wish]:
        wish_list_pk = self.kwargs["wish_list_id"]
        wish_list = get_object_or_404(WishList, id=wish_list_pk)
        have_access = AvailableWishList.objects.filter(
            wish_list=wish_list, user_id=self.request.user.id
        )

        if not have_access:
            return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))

        status = self.request.GET.get("status") == "fulfilled"
        wishes = Wish.objects.filter(wish_list=wish_list, fulfilled=status)
        return wishes

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        wish_list_pk = self.kwargs["wish_list_id"]
        wish_list = get_object_or_404(WishList, id=wish_list_pk)
        status = self.request.GET.get("status") == "fulfilled"
        active_count = (Wish.objects.filter(wish_list=wish_list, fulfilled=False).count(),)
        fulfilled_count = (Wish.objects.filter(wish_list=wish_list, fulfilled=True).count(),)

        context["wish_list"] = wish_list
        context["show_fulfilled"] = status
        context["active_count"] = active_count
        context["fulfilled_count"] = fulfilled_count

        return context
