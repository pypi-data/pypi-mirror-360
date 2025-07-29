# vipps_auth/urls.py

from django.urls import path
from . import views

# These patterns are for the standard browser-based OAuth flow.
# A consuming project can include these URLs, for example, under `/accounts/`.
# Path: /accounts/vipps/login/ -> redirects to Vipps
# Path: /accounts/vipps/login/callback/ -> handles the return from Vipps
urlpatterns = [
    path("vipps/login/", views.vipps_login, name="vipps_login"),
    path("vipps/login/callback/", views.vipps_callback, name="vipps_callback"),
]