
"""Интеграция Kerberos-аутентификации с OIDC Authorization Endpoint."""

from urllib.parse import urlsplit, urlunsplit

from django.contrib.auth.views import redirect_to_login
from django.core import signing
from django.http import QueryDict
from django.shortcuts import resolve_url

from oauth2_provider.views import AuthorizationView


class KerberosAuthorizationView(AuthorizationView):
    """Расширение стандартного OIDC Authorization Endpoint."""

    def handle_prompt_login(self):
        """Перенаправляет пользователя на Kerberos-вход."""

        # Получаем исходные параметры OIDC-запроса.
        query = self.request.GET.copy()

        # Удаляем login из списка prompt, сохраняя остальные значения.
        prompts = query.get("prompt", "").split()
        prompts = [value for value in prompts if value != "login"]

        if prompts:
            query["prompt"] = " ".join(prompts)
        else:
            query.pop("prompt", None)

        # Сохраняем исходный адрес Authorization Endpoint.
        next_url = self.request.path_info

        if query:
            next_url += "?" + query.urlencode()

        # Создаём подписанный признак повторной аутентификации.
        challenge = signing.dumps(
            {"reauthenticate": True},
            salt="identity.kerberos.reauthentication",
            compress=True,
        )

        # Добавляем признак к адресу страницы входа.
        login_url = resolve_url(self.get_login_url())
        parts = urlsplit(login_url)

        login_query = QueryDict(parts.query, mutable=True)
        login_query["kerberos_reauth"] = challenge

        login_url = urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                login_query.urlencode(),
                parts.fragment,
            )
        )

        # Используем штатный механизм Django для передачи next.
        return redirect_to_login(
            next_url,
            login_url,
            self.get_redirect_field_name(),
        )
