"""
Модуль проверки Kerberos-билетов с использованием GSSAPI.

Принимает декодированный SPNEGO-токен, проверяет его
на стороне сервера и возвращает подтверждённый Kerberos principal.

Сопоставление principal с пользователем Django выполняется отдельно.
"""

import logging
from dataclasses import dataclass

from django.conf import settings

try:
    import gssapi
    from gssapi.exceptions import GSSError
except (ImportError, OSError):
    gssapi = None
    GSSError = Exception

from .exceptions import (
    KerberosAuthenticationError,
    KerberosConfigurationError,
    KerberosContextIncomplete,
    KerberosTokenError,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KerberosAuthenticationResult:
    """Результат успешной проверки Kerberos-билета."""

    principal: str
    response_token: bytes | None = None


def authenticate_kerberos_token(token: bytes) -> KerberosAuthenticationResult:
    """
    Проверяет входящий Kerberos/SPNEGO-токен.

    Аргументы:
        token: декодированный токен заголовка Authorization.

    Возвращает:
        Результат проверки с подтверждённым principal.

    Исключения:
        KerberosTokenError: некорректный входящий токен.
        KerberosConfigurationError: ошибка конфигурации сервера.
        KerberosContextIncomplete: обмен токенами не завершён.
        KerberosAuthenticationError: билет не прошёл проверку.
    """

    if not isinstance(token, bytes) or not token:
        raise KerberosTokenError(
            "Не передан корректный Kerberos-токен."
        )

    if gssapi is None:
        raise KerberosConfigurationError(
            "Библиотека python-gssapi не установлена."
        )

    keytab_path = getattr(settings, "KERBEROS_KEYTAB", None)
    service_principal = getattr(
        settings,
        "KERBEROS_SERVICE_PRINCIPAL",
        None,
    )

    if not keytab_path or not service_principal:
        raise KerberosConfigurationError(
            "Не настроены путь к keytab или Service Principal Name."
        )

    try:
        service_name = gssapi.Name(
            service_principal,
            name_type=gssapi.NameType.kerberos_principal,
        )

        credentials = gssapi.Credentials(
            name=service_name,
            usage="accept",
            mechs=[gssapi.MechType.kerberos],
            store={
                "keytab": keytab_path,
            },
        )

        context = gssapi.SecurityContext(
            creds=credentials,
            usage="accept",
        )

        response_token = context.step(token)

        if not context.complete:
            raise KerberosContextIncomplete(
                "Kerberos-обмен требует дополнительного шага."
            )

        if context.mech != gssapi.MechType.kerberos:
            raise KerberosAuthenticationError(
                "Использован неподдерживаемый механизм аутентификации."
            )

        if context.initiator_name is None:
            raise KerberosAuthenticationError(
                "Kerberos не вернул имя пользователя."
            )

        principal = str(context.initiator_name)

        if not principal or "@" not in principal:
            raise KerberosAuthenticationError(
                "Получено некорректное имя Kerberos-пользователя."
            )

        _, realm = principal.rsplit("@", 1)

        if realm.upper() != settings.KERBEROS_REALM.upper():
            raise KerberosAuthenticationError(
                "Kerberos principal принадлежит другому домену."
            )

        return KerberosAuthenticationResult(
            principal=principal,
            response_token=response_token,
        )

    except (
            KerberosTokenError,
            KerberosConfigurationError,
            KerberosContextIncomplete,
            KerberosAuthenticationError,
    ):
        raise

    except GSSError as error:
        logger.warning(
            "GSSAPI отклонил Kerberos-токен: %s",
            type(error).__name__,
        )
        raise KerberosAuthenticationError(
            "Не удалось проверить Kerberos-билет."
        ) from error

    except (OSError, RuntimeError) as error:
        logger.exception(
            "Ошибка получения серверных Kerberos credentials."
        )
        raise KerberosConfigurationError(
            "Не удалось получить серверные Kerberos credentials."
        ) from error
