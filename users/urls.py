from typing import Final

from django.urls import path

from users import views

app_name: Final[str] = "users"
urlpatterns = [
    path("sign-up/", views.UserSignUp.as_view(), name="sign_up"),
    path("sign-in/", views.UserSignIn.as_view(), name="sign_in"),
    path("profile/", views.UserProfile.as_view(), name="profile"),
]
