
from django.urls import path

from . import views


urlpatterns = [
    # Автоматический вход сотрудников через Kerberos.
    path(
        "",
        views.KerberosLoginView.as_view(),
        name="login",
    ),

    # Локальный вход только для superuser.
    path(
        "local-login/",
        views.UserLoginView.as_view(),
        name="local_login",
    ),

    # Завершение общей Django-сессии.
    path(
        "logout/",
        views.UserLogoutView.as_view(),
        name="logout",
    ),
]
