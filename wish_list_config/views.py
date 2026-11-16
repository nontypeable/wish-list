from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.views.decorators.http import require_safe

if TYPE_CHECKING:
    from django.http import HttpRequest


@require_safe
def healthcheck(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")
