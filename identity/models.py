from uuid import UUID

from django.contrib.auth.models import User
from uuid_utils import uuid7

from django.conf import settings
from django.db import models


def generate_uuid7():
    return UUID(str(uuid7()))


class UserIdentity(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="identity",
        verbose_name="Пользователь Django",
    )

    subject = models.UUIDField(
        default=generate_uuid7,
        unique=True,
        editable=False,
        verbose_name="Уникальный идентификатор пользователя (OIDC Subject)",
    )

    ad_object_guid = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="Уникальный идентификатор учётной записи AD (Object GUID)",
    )

    ad_login = models.CharField(
        max_length=150,
        blank=True,
        unique=True,
        null=True,
        verbose_name="Логин пользователя в Active Directory",
    )

    ad_email = models.EmailField(
        blank=True,
        verbose_name="Корпоративный email из Active Directory",
    )

    ad_linked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата привязки к Active Directory",
    )

    ad_last_synced = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата последней синхронизации с Active Directory",
    )

    allow_ad_login = models.BooleanField(
        default=True,
        verbose_name="Разрешён вход через Active Directory",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания записи",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего изменения записи",
    )

    class Meta:
        verbose_name = "Идентификатор пользователя"
        verbose_name_plural = "Идентификаторы пользователей"

    def __str__(self):
        return f"{self.user.username} ({self.subject})"


class EmployeeModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name="Пользователь",
        related_name="auth_employee",
    )
    last_name = models.CharField("Фамилия", max_length=150)
    first_name = models.CharField("Имя", max_length=150)
    middle_name = models.CharField("Отчество", max_length=150)
    personnel_number = models.CharField("Табельный номер", max_length=20, null=True, default=None)

    work_status = models.BooleanField(
        verbose_name="Сотрудник работает",
        default=True,
    )

    class Meta:
        managed = False
        verbose_name = "сотрудник"
        verbose_name_plural = "сотрудники"
        db_table = 'ToDo_tasks_employee'
