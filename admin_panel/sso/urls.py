# sso/urls.py
from django.urls import path
from .views import jwt_login, jwt_logout

urlpatterns = [
    path("login/", jwt_login, name="sso_login"),
    path("logout/", jwt_logout, name="sso_logout"),
]
