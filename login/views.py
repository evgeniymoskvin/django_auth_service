
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from . import forms


class UserLoginView(LoginView):
    """Локальный вход для суперпользователя."""

    form_class = forms.LoginForm
    template_name = "login/login.html"
    redirect_authenticated_user = True


class KerberosLoginView(LoginView):
    """Точка входа сотрудников через Kerberos."""

    template_name = "login/kerberos_login.html"
    redirect_authenticated_user = False

    def get(self, request, *args, **kwargs):
        """
        Передаёт запрос middleware для запуска Kerberos-аутентификации.
        """
        return super().get(request, *args, **kwargs)


class UserLogoutView(LogoutView):
    """Завершение текущей Django-сессии."""



