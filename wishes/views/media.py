from pathlib import Path
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.urls import reverse_lazy
from django.views.decorators.http import require_safe

from wishes.models import Wish

if TYPE_CHECKING:
    from wishes.views.wishes import AuthenticatedHttpRequest


@login_required(login_url=reverse_lazy("users:sign_in"))
@require_safe
def wish_image(request: AuthenticatedHttpRequest, image_path: str) -> FileResponse:
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
