"""
Аутентификация пользователей через Active Directory.

Новые Django User не создаются.
"""

from django.conf import settings
from django.utils import timezone

from ldap3 import Server, Connection, NONE
from ldap3.core.exceptions import LDAPException
from ldap3 import SUBTREE
from ldap3.utils.conv import escape_filter_chars

from .models import UserIdentity
from .access import is_employee_allowed

from django.db import transaction

AD_USER_ATTRIBUTES = [
    "objectGUID",  # Постоянный идентификатор
    "sAMAccountName",  # Доменный логин
    "userPrincipalName",  # Логин вида user@domain
    "mail",  # Корпоративная почта
]


def get_ad_linked_user(ad_object_guid=None, ad_login=None):
    """
    Находит существующего Django User,
    связанного с учётной записью Active Directory.
    """

    if not ad_object_guid and not ad_login:
        return None

    identity = None

    if ad_object_guid:
        identity = (
            UserIdentity.objects
            .select_related("user")
            .filter(ad_object_guid=ad_object_guid)
            .first()
        )

    if identity is None and ad_login:
        identity = (
            UserIdentity.objects
            .select_related("user")
            .filter(ad_login__iexact=ad_login)
            .first()
        )

    if identity is None:
        return None

    if not identity.allow_ad_login:
        return None

    if not is_employee_allowed(identity.user):
        return None

    return identity.user


def authenticate_ad_credentials(username, password):
    """
    Проверяет логин и пароль пользователя в Active Directory.

    Возвращает данные AD при успешной проверке.
    """

    if not settings.AD_ENABLED:
        return None

    if not username or not password or not settings.AD_SERVER:
        return None

    server = Server(
        settings.AD_SERVER,
        use_ssl=settings.AD_USE_SSL,
        connect_timeout=settings.AD_CONNECT_TIMEOUT,
        get_info=NONE,
    )

    try:
        connection = Connection(
            server,
            user=username,
            password=password,
            receive_timeout=settings.AD_RECEIVE_TIMEOUT,
            auto_bind=True,
        )

        try:
            ad_user = search_ad_user(connection, username)

            if ad_user is None:
                return None

            return ad_user

        finally:
            connection.unbind()

    except LDAPException:
        return None


def authenticate_ad_user(username, password):
    """
    Полная AD-аутентификация.
    Возвращает существующего Django User либо None.
    """

    ad_user = authenticate_ad_credentials(username, password)

    if ad_user is None:
        return None

    # Сначала проверяем, существует ли привязка по GUID.
    identity = UserIdentity.objects.filter(
        ad_object_guid=ad_user["object_guid"]
    ).select_related("user").first()

    if identity is not None:
        if not identity.allow_ad_login:
            return None

        if not is_employee_allowed(identity.user):
            return None

        return identity.user

    # Если GUID ещё не привязан, допускаем первоначальную привязку.
    return link_ad_user_by_email(ad_user)



def convert_ad_guid(value):
    """
    Преобразует objectGUID из Active Directory в UUID.
    """

    from uuid import UUID

    if isinstance(value, bytes):
        return UUID(bytes_le=value)

    if isinstance(value, str):
        return UUID(value)

    return None


def search_ad_user(connection, username):
    """
    Ищет пользователя в Active Directory.

    Возвращает:
        dict с атрибутами AD;
        None, если пользователь не найден.
    """

    base_dn = settings.AD_BASE_DN

    if not base_dn:
        return None

    search_filter = (
        f"(&(objectCategory=person)"
        f"(objectClass=user)"
        f"(sAMAccountName={escape_filter_chars(username)}))"
    )

    connection.search(
        search_base=base_dn,
        search_filter=search_filter,
        search_scope=SUBTREE,
        attributes=AD_USER_ATTRIBUTES,
    )

    if len(connection.entries) != 1:
        return None

    entry = connection.entries[0]

    return {
        "object_guid": convert_ad_guid(entry.objectGUID.raw_values[0]),
        "login": str(entry.sAMAccountName.value),
        "upn": str(entry.userPrincipalName.value or ""),
        "email": str(entry.mail.value or ""),
    }


def link_ad_account(user, ad_user):
    """
    Привязывает AD-учётную запись
    к существующему Django UserIdentity.
    """

    identity = UserIdentity.objects.filter(user=user).first()

    if identity is None:
        return False

    ad_object_guid = ad_user["object_guid"]
    ad_login = ad_user["login"]
    ad_email = ad_user["email"]

    if not ad_object_guid:
        return False

    # Проверяем, не привязан ли GUID к другому пользователю.
    guid_exists = UserIdentity.objects.filter(
        ad_object_guid=ad_object_guid
    ).exclude(user=user).exists()

    if guid_exists:
        return False

    identity.ad_object_guid = ad_object_guid
    identity.ad_login = ad_login
    identity.ad_email = ad_email
    identity.ad_linked_at = timezone.now()
    identity.ad_last_synced = timezone.now()

    identity.save(update_fields=[
        "ad_object_guid",
        "ad_login",
        "ad_email",
        "ad_linked_at",
        "ad_last_synced",
        "updated_at",
    ])

    return True


@transaction.atomic
def link_ad_user_by_email(ad_user):
    """
    Первоначально связывает AD-учётную запись
    с существующим Django User по корпоративной почте.

    Новые Django User не создаются.
    """

    ad_object_guid = ad_user.get("object_guid")
    ad_login = ad_user.get("login")
    ad_email = ad_user.get("email")

    if not ad_object_guid or not ad_login or not ad_email:
        return None

    # Ищем существующего Django User по email.
    from django.contrib.auth import get_user_model

    User = get_user_model()

    users = User.objects.filter(
        email__iexact=ad_email
    )

    if users.count() != 1:
        return None

    user = users.first()

    # Проверяем, что пользователь является работающим сотрудником.
    if not is_employee_allowed(user):
        return None

    # Получаем существующую запись идентификатора.
    identity = (
        UserIdentity.objects
        .select_for_update()
        .filter(user=user)
        .first()
    )

    if identity is None:
        return None

    # Не перезаписываем уже существующую привязку.
    if identity.ad_object_guid:
        return None

    if identity.ad_login:
        return None

    if not identity.allow_ad_login:
        return None

    # Проверяем, не привязан ли GUID к другому пользователю.
    if UserIdentity.objects.filter(
            ad_object_guid=ad_object_guid
    ).exists():
        return None

    from django.utils import timezone

    now = timezone.now()

    identity.ad_object_guid = ad_object_guid
    identity.ad_login = ad_login
    identity.ad_email = ad_email
    identity.ad_linked_at = now
    identity.ad_last_synced = now

    identity.save(update_fields=[
        "ad_object_guid",
        "ad_login",
        "ad_email",
        "ad_linked_at",
        "ad_last_synced",
        "updated_at",
    ])

    return user
