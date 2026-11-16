from pathlib import Path
from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import FileResponse, Http404
from django.urls import reverse_lazy
from django.views import View

from wishes.models import Wish

if TYPE_CHECKING:
    from wishes.views.wishes import AuthenticatedHttpRequest


class WishImage(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:sign_in")
    http_method_names = ("get", "head")

    def get(self, request: AuthenticatedHttpRequest, image_path: str) -> FileResponse:
        wish = (
            Wish.objects.filter(image=image_path)
            .filter(Q(wish_list__user=request.user) | Q(wish_list__accesses__user=request.user))
            .first()
        )
        if wish is None:
            raise Http404("Изображение не найдено.")
        try:
            image = wish.image.open("rb")
        except FileNotFoundError:
            raise Http404("Изображение не найдено.") from None
        response = FileResponse(image, filename=Path(image_path).name)
        response["Cache-Control"] = "private, no-store"
        return response
