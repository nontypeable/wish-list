from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from wishes.views import invitations, wishes

app_name = "wishes"
urlpatterns = [
    path("", wishes.GetWishList.as_view(), name="get_wish_list"),
    path("<int:wish_list_id>/", wishes.OpenWish.as_view(), name="open_other_wish_list"),
    path("create/", wishes.CreateWish.as_view(), name="create_wish"),
    path("fulfill/<int:wish>", wishes.FulfillWish.as_view(), name="fulfill_wish"),
    path("book/<int:wish>", wishes.BookWish.as_view(), name="book_wish"),
    path("unbook/<int:wish>", wishes.UnBookWish.as_view(), name="unbook_wish"),
    path("invantions/new", invitations.CreateInvitation.as_view(), name="create_invitation"),
    path("invantions/<str:code>", invitations.AcceptInvitation.as_view(), name="accept_invitation"),
    path("wishlists/shared", invitations.GetAcceptedWishLists.as_view(), name="shared_wishlists"),
    path("access/", invitations.ManageAccess.as_view(), name="manage_access"),
    path(
        "access/not-ready/",
        login_required(
            TemplateView.as_view(template_name="wishes/invitations/not_ready.html"),
            login_url="users:sign_in",
        ),
        name="access_not_ready",
    ),
]
