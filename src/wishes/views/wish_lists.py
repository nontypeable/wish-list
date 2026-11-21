from typing import TYPE_CHECKING, Any, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView

from wishes.models import AvailableWishList, Wish, WishList

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http.request import HttpRequest
    from django.http.response import HttpResponse

    from wishes.views._types import AuthenticatedHttpRequest


class MyWishListView(LoginRequiredMixin, ListView):
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


class SharedWishListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("users:sign_in")
    model = Wish
    context_object_name = "wishes"
    template_name = "wishes/shared_wish_list.html"

    def get_queryset(self) -> QuerySet[Wish]:
        self.wish_list = get_object_or_404(
            WishList,
            pk=self.kwargs["wish_list_id"],
        )

        is_owner = self.wish_list.user_id == self.request.user.pk
        is_invited = AvailableWishList.objects.filter(
            wish_list_id=self.wish_list.pk,
            user_id=self.request.user.pk,
        ).exists()

        if not (is_owner or is_invited):
            raise PermissionDenied("Нет доступа к этому вишлисту.")

        status = self.request.GET.get("status") == "fulfilled"
        wishes = Wish.objects.filter(wish_list__id=self.wish_list.pk, fulfilled=status)
        return wishes

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        wish_list_pk = self.kwargs["wish_list_id"]
        wish_list = WishList.objects.get(pk=wish_list_pk)
        status = self.request.GET.get("status") == "fulfilled"
        active_count = (Wish.objects.filter(wish_list__id=wish_list_pk, fulfilled=False).count(),)
        fulfilled_count = (Wish.objects.filter(wish_list__id=wish_list_pk, fulfilled=True).count(),)

        context["wish_list"] = wish_list
        context["show_fulfilled"] = status
        context["active_count"] = active_count
        context["fulfilled_count"] = fulfilled_count

        return context


class AccessibleWishListsView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")

    def get(self, request: AuthenticatedHttpRequest) -> HttpResponse:
        wish_lists = (
            WishList.objects.filter(accesses__user=request.user).select_related("user").distinct()
        )
        return render(
            request,
            "wishes/available_wish_lists.html",
            {"shared_wish_lists": wish_lists},
        )

    post = get
    put = get
    patch = get
    delete = get
    trace = get

    def options(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.get(cast("AuthenticatedHttpRequest", request))
