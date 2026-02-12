from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sso/", include("sso.urls")),
    path("health", health),
]
