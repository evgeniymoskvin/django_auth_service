from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from identity.models import EmployeeModel, UserIdentity


class Command(BaseCommand):
    help = "Создание UserIdentity для сотрудников из справочника"

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0
        error_count = 0

        employees = EmployeeModel.objects.select_related("user").all()

        total = employees.count()

        self.stdout.write(f"Найдено сотрудников: {total}")

        for employee in employees:
            try:
                with transaction.atomic():
                    _, created = UserIdentity.objects.get_or_create(
                        user_id=employee.user_id
                    )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Создан UserIdentity: {employee.user.username}"
                        )
                    )
                else:
                    existing_count += 1

            except IntegrityError as error:
                error_count += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"Ошибка для user_id={employee.user_id}: {error}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Синхронизация завершена"))
        self.stdout.write(f"Создано: {created_count}")
        self.stdout.write(f"Уже существовало: {existing_count}")
        self.stdout.write(f"Ошибок: {error_count}")

# Для запуска:
# python manage.py sync_user_identities