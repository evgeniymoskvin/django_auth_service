
"""Сопоставление Kerberos principal с существующим пользователем Django.

Поиск выполняется по UPN, а затем по логину Active Directory.
Создание новых пользователей и записей UserIdentity не выполняется.
"""

from django.conf import settings

from identity.models import UserIdentity
from identity.access import is_employee_allowed

from .exceptions import KerberosIdentityError


def normalize_principal(principal: str) -> str:
    """Нормализует Kerberos principal для сопоставления с AD-данными."""
    if not isinstance(principal, str) or not principal.strip():
        raise KerberosIdentityError(
            "Не передано имя Kerberos-пользователя."
        )

    principal = principal.strip()

    if "@" not in principal:
        raise KerberosIdentityError(
            "Kerberos principal имеет некорректный формат."
        )

    login, realm = principal.rsplit("@", 1)

    if not login or not realm:
        raise KerberosIdentityError(
            "Kerberos principal имеет некорректный формат."
        )

    if realm.upper() != settings.KERBEROS_REALM.upper():
        raise KerberosIdentityError(
            "Kerberos principal принадлежит другому домену."
        )

    return login.strip().lower()


def get_user_by_kerberos_principal(principal: str):
    """Находит и проверяет существующего пользователя Django.

    Порядок поиска:
        1. По полному UPN.
        2. По sAMAccountName.

    Возвращает:
        Существующий объект Django User.

    Исключения:
        KerberosIdentityError — пользователь не найден
        или не прошёл проверку допуска.
    """
    if not isinstance(principal, str) or not principal.strip():
        raise KerberosIdentityError(
            "Не передано имя Kerberos-пользователя."
        )

    principal = principal.strip()

    if "@" not in principal:
        raise KerberosIdentityError(
            "Kerberos principal имеет некорректный формат."
        )

    login, realm = principal.rsplit("@", 1)

    if not login or not realm:
        raise KerberosIdentityError(
            "Kerberos principal имеет некорректный формат."
        )

    if realm.upper() != settings.KERBEROS_REALM.upper():
        raise KerberosIdentityError(
            "Kerberos principal принадлежит другому домену."
        )

    upn = f"{login}@{realm}"

    try:
        identity = UserIdentity.objects.select_related(
            "user"
        ).get(ad_upn__iexact=upn)

    except UserIdentity.DoesNotExist:
        try:
            identity = UserIdentity.objects.select_related(
                "user"
            ).get(ad_login__iexact=login)

        except UserIdentity.DoesNotExist:
            raise KerberosIdentityError(
                "Для Kerberos-пользователя не найдена связанная учётная запись."
            )

        except UserIdentity.MultipleObjectsReturned:
            raise KerberosIdentityError(
                "Найдено несколько учётных записей для Kerberos-пользователя."
            )

    except UserIdentity.MultipleObjectsReturned:
        raise KerberosIdentityError(
            "Найдено несколько учётных записей для Kerberos-пользователя."
        )

    if not identity.allow_ad_login:
        raise KerberosIdentityError(
            "Вход через Active Directory запрещён."
        )

    if not is_employee_allowed(identity.user):
        raise KerberosIdentityError(
            "Пользователь не прошёл проверку допуска приложения."
        )

    return identity.user
