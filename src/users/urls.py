from typing import Final

from django.urls import path

from users import views

app_name: Final[str] = "users"
urlpatterns = [
    path("sign-up/", views.SignUpView.as_view(), name="sign_up"),
    path("sign-in/", views.SignInView.as_view(), name="sign_in"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
]
