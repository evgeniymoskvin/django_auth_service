from django.urls import path
from . import views

urlpatterns = [
    path("ad-login/", views.ad_login_view, name="ad_login"),
]