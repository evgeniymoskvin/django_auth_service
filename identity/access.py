from django.contrib.auth import get_user_model

from .models import EmployeeModel


User = get_user_model()


def is_employee_allowed(user):
    """
    Проверяет, разрешён ли сотруднику вход в Auth Service.

    Условия:
    1. Пользователь должен быть авторизован.
    2. User.is_active должен быть True.
    3. Пользователь должен присутствовать в кадровом справочнике (в таблице EmployeeModel).
    4. EmployeeModel.work_status должен быть True.
    """

    if not user or not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    return EmployeeModel.objects.filter(
        user_id=user.pk,
        work_status=True,
    ).exists()