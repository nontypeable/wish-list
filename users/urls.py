from typing import Final

from django.urls import path

from users import views

app_name: Final[str] = "users"
urlpatterns = [
    path("sign-up/", views.sign_up, name="sign_up"),
    path("sign-in/", views.sign_in, name="sign_in"),
    path("profile/", views.profile, name="profile"),
]
