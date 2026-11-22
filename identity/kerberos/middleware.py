
"""
Middleware автоматической Kerberos-аутентификации.

Kerberos применяется только на странице входа Auth Service.
После успешной проверки билета пользователь авторизуется
через стандартную Django-сессию.

Middleware не создаёт пользователей и не изменяет OIDC-процесс.
"""

import base64
import binascii
import logging

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from .policy import should_use_kerberos
from django.utils.http import url_has_allowed_host_and_scheme

from .authentication import authenticate_kerberos_token
from .exceptions import (
    KerberosAuthenticationError,
    KerberosConfigurationError,
    KerberosContextIncomplete,
    KerberosIdentityError,
    KerberosTokenError,
)
from .identity import get_user_by_kerberos_principal


logger = logging.getLogger(__name__)


class KerberosAuthenticationMiddleware:
    """
    Обрабатывает автоматический вход пользователей через Kerberos.

    Middleware должен располагаться после AuthenticationMiddleware.
    """

    authentication_backend = (
        "django.contrib.auth.backends.ModelBackend"
    )

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        try:
            use_kerberos = should_use_kerberos(request)

        except KerberosAuthenticationError:
            logger.warning(
                "Отклонён недействительный запрос повторной Kerberos-аутентификации."
            )
            return HttpResponse(
                "Invalid Kerberos reauthentication request.",
                status=403,
            )

        if not use_kerberos:
            return self.get_response(request)

        authorization = request.headers.get("Authorization", "")


        # Если браузер ещё не передал билет, запрашиваем Negotiate.
        if not authorization:
            return self._negotiate_challenge()

        # Разбираем схему HTTP-аутентификации.
        scheme, separator, encoded_token = authorization.partition(" ")

        if (
            scheme.lower() != "negotiate"
            or not separator
            or not encoded_token.strip()
        ):
            return self._negotiate_challenge()

        try:
            # Ограничиваем размер входящего токена.
            encoded_token = encoded_token.strip()

            if len(encoded_token) > 90000:
                raise KerberosTokenError(
                    "Размер Kerberos-токена превышает допустимый."
                )

            # Декодируем Base64-токен.
            token = base64.b64decode(
                encoded_token,
                validate=True,
            )

            # Проверяем Kerberos-билет.
            result = authenticate_kerberos_token(token)

            # Находим существующего сотрудника Django.
            user = get_user_by_kerberos_principal(
                result.principal
            )

            # Создаём стандартную Django-сессию.
            login(
                request,
                user,
                backend=self.authentication_backend,
            )

            # Возвращаем пользователя к исходному OIDC-запросу.
            response = self._redirect_after_login(request)

            # При наличии ответного токена передаём его браузеру.
            if result.response_token:
                response["WWW-Authenticate"] = (
                    "Negotiate "
                    + base64.b64encode(
                        result.response_token
                    ).decode("ascii")
                )

            return response

        except KerberosContextIncomplete:
            # Продолжение многошагового обмена пока не реализовано.
            logger.warning(
                "Kerberos-контекст не завершился за один запрос."
            )
            return HttpResponse(
                "Kerberos negotiation is incomplete.",
                status=503,
            )

        except KerberosConfigurationError:
            logger.exception(
                "Ошибка конфигурации Kerberos."
            )
            return HttpResponse(
                "Kerberos authentication is temporarily unavailable.",
                status=503,
            )

        except KerberosIdentityError:
            logger.warning(
                "Kerberos-пользователь не прошёл проверку допуска."
            )
            return HttpResponse(
                "Access denied.",
                status=403,
            )

        except (
            KerberosTokenError,
            KerberosAuthenticationError,
            binascii.Error,
            ValueError,
        ):
            logger.warning(
                "Kerberos-аутентификация не пройдена."
            )
            return self._negotiate_challenge()

    def _negotiate_challenge(self):
        """
        Запрашивает у браузера Kerberos-аутентификацию.
        """

        response = HttpResponse(status=401)
        response["WWW-Authenticate"] = "Negotiate"
        response["Cache-Control"] = "no-store"

        return response


    def _redirect_after_login(self, request):
        """
        Возвращает пользователя к исходному адресу после входа.
        Проверяет безопасность адреса перенаправления.
        """

        redirect_to = (
            request.POST.get("next")
            or request.GET.get("next")
            or resolve_url(settings.LOGIN_REDIRECT_URL)
        )

        allowed_hosts = {request.get_host()}

        if not url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=allowed_hosts,
            require_https=request.is_secure(),
        ):
            redirect_to = resolve_url(
                settings.LOGIN_REDIRECT_URL
            )

        return HttpResponseRedirect(redirect_to)

