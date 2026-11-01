
from django.contrib import admin

from .models import UserIdentity, EmployeeModel


@admin.register(UserIdentity)
class UserIdentityAdmin(admin.ModelAdmin):

    list_display = ("user","subject","ad_login","ad_email","allow_ad_login","ad_linked_at",)

    list_display_links = ("user","subject",)

    list_filter = ("allow_ad_login","ad_linked_at",)

    search_fields = ("user__username","user__email","ad_login","ad_email","subject","ad_object_guid",)

    readonly_fields = (
        "subject",
        "ad_object_guid",
        "ad_login",
        "ad_email",
        "ad_linked_at",
        "ad_last_synced",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Пользователь",
            {
                "fields": (
                    "user",
                    "subject",
                )
            },
        ),
        (
            "Active Directory",
            {
                "fields": (
                    "ad_object_guid",
                    "ad_login",
                    "ad_email",
                    "allow_ad_login",
                    "ad_linked_at",
                    "ad_last_synced",
                )
            },
        ),
        (
            "Системная информация",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    ordering = ("user__username",)

# admin.site.register(EmployeeModel, EmployeeAdmin)
@admin.register(EmployeeModel)
class EmployeeAdmin(admin.ModelAdmin):

    ordering = ["-work_status", "last_name", "first_name", "middle_name"]
    search_fields = ["last_name", "first_name", "middle_name", "personnel_number"]
    list_display = ("last_name", "first_name", "middle_name", "personnel_number", 'work_status')
