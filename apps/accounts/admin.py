from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "username",
        "email",
        "role",
        "is_active",
        "is_staff",
        "created_at",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_email_verified",
    )

    search_fields = (
        "username",
        "email",
        "phone_number",
    )

    ordering = ("-created_at",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Healthcare Information",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "date_of_birth",
                    "is_email_verified",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Healthcare Information",
            {
                "fields": (
                    "email",
                    "role",
                    "phone_number",
                    "date_of_birth",
                )
            },
        ),
    )