from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView

from wishes.forms import CreateWishForm
from wishes.models import Wish, WishList

if TYPE_CHECKING:
    from django.http.response import HttpResponse

    from wishes.views._types import AuthenticatedHttpRequest

    BaseWishCreateView = CreateView[Wish, CreateWishForm]
else:
    BaseWishCreateView = CreateView


class WishCreateView(LoginRequiredMixin, BaseWishCreateView):
    request: AuthenticatedHttpRequest

    model = Wish
    form_class = CreateWishForm
    login_url = reverse_lazy("users:sign_in")
    template_name = "wishes/create_wish.html"
    success_url = reverse_lazy("wishes:get_wish_list")

    def form_valid(self, form: CreateWishForm) -> HttpResponse:
        form.instance.wish_list = WishList.objects.get(user=self.request.user)
        return super().form_valid(form)


class WishFulfillView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def post(self, request: AuthenticatedHttpRequest, wish: int) -> HttpResponse:
        selected_wish = get_object_or_404(Wish, id=wish, wish_list__user=request.user)
        selected_wish.fulfilled = True
        selected_wish.save(update_fields=["fulfilled"])
        return HttpResponseRedirect(reverse_lazy("wishes:get_wish_list"))
