from django.urls import path

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
]
