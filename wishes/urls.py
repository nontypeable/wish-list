from django.urls import path

from wishes.views import wishes

app_name = "wishes"
urlpatterns = [
    path("", wishes.get_wish_list, name="get_wish_list"),
    path("create/", wishes.create_wish, name="create_wish"),
    path("fulfill/<int:wish>", wishes.fulfill_wish, name="fulfill_wish"),
]
