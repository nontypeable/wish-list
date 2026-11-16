from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from wishes.views import invitations, wishes

app_name = "wishes"
urlpatterns = [
    path("", wishes.get_wish_list, name="get_wish_list"),
    path("<int:wish_list_id>/", wishes.open_wish, name="open_other_wish_list"),
    path("create/", wishes.create_wish, name="create_wish"),
    path("fulfill/<int:wish>", wishes.fulfill_wish, name="fulfill_wish"),
    path("invantions/new", invitations.create_invitation, name="create_invitation"),
    path("invantions/<str:code>", invitations.accept_invitation, name="accept_invitation"),
    path("wishlists/shared", invitations.get_accepted_wish_lists, name="shared_wishlists"),
    path("access/", invitations.manage_access, name="manage_access"),
    path(
        "access/not-ready/",
        login_required(
            TemplateView.as_view(template_name="wishes/invitations/not_ready.html"),
            login_url="users:sign_in",
        ),
        name="access_not_ready",
    ),
]
