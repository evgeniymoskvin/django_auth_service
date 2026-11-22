
"""
Правила запуска Kerberos-аутентификации.
"""

import logging

from django.conf import settings
from django.core import signing
from django.shortcuts import resolve_url

from .exceptions import KerberosAuthenticationError


logger = logging.getLogger(__name__)

# Максимальное время действия запроса повторной аутентификации.
KERBEROS_REAUTH_MAX_AGE = 120

# Соль для проверки подписанного признака.
KERBEROS_REAUTH_SALT = (
    "identity.kerberos.reauthentication"
)


def should_use_kerberos(request):
    """
    Определяет, требуется ли Kerberos-аутентификация.

    При наличии подписанного признака повторной аутентификации
    Kerberos запускается даже при существующей Django-сессии.
    """

    if not getattr(settings, "KERBEROS_ENABLED", False):
        return False

    login_path = resolve_url(settings.LOGIN_URL).split("?")[0]

    if request.path_info != login_path:
        return False

    challenge = request.GET.get("kerberos_reauth")

    # Повторная аутентификация имеет приоритет над существующей сессией.
    if challenge is not None:
        if not requires_kerberos_reauthentication(request):
            raise KerberosAuthenticationError(
                "Запрос повторной Kerberos-аутентификации "
                "недействителен или просрочен."
            )

        return True

    # При обычном входе существующей сессии достаточно.
    if request.user.is_authenticated:
        return False

    return True



def requires_kerberos_reauthentication(request):
    """
    Проверяет подписанный запрос принудительной Kerberos-аутентификации.

    Возвращает True, если подпись корректна и срок действия
    запроса не превышает установленный предел.
    """

    challenge = request.GET.get("kerberos_reauth")

    if not challenge:
        return False

    try:
        payload = signing.loads(
            challenge,
            salt=KERBEROS_REAUTH_SALT,
            max_age=KERBEROS_REAUTH_MAX_AGE,
        )

    except signing.SignatureExpired:
        logger.warning(
            "Истёк срок действия запроса повторной Kerberos-аутентификации."
        )
        return False

    except signing.BadSignature:
        logger.warning(
            "Получен некорректный запрос повторной Kerberos-аутентификации."
        )
        return False

    return (
        isinstance(payload, dict)
        and payload.get("reauthenticate") is True
    )
