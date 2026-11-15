from django.urls import path

from wishes import views

app_name = "wishes"
urlpatterns = [
    path("", views.get_wish_list, name="get_wish_list"),
    path("create/", views.create_wish, name="create_wish"),
    path("fulfill/<int:wish>", views.fulfill_wish, name="fulfill_wish"),
]
