"""
URL configuration for wish_list_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from django.views.generic import TemplateView

from wish_list_config.views import healthcheck
from wishes.views.media import wish_image

urlpatterns: list[URLPattern | URLResolver] = [
    path("healthz/", healthcheck, name="healthcheck"),
    path("media/<path:image_path>", wish_image, name="wish_image"),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("users/", include("users.urls"), name="users"),
    path("wishes/", include("wishes.urls"), name="wishes"),
    path("admin/", admin.site.urls),
]
