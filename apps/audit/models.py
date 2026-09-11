from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        VIEW = "VIEW", "View"
        AI_QUERY = "AI_QUERY", "AI Query"
        AI_ACTION = "AI_ACTION", "AI Action"
        AI_CONFIRM = "AI_CONFIRM", "AI Confirmation"
        UPLOAD = "UPLOAD", "Upload"
        CANCEL = "CANCEL", "Cancel"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=30,
        choices=Action.choices,
        db_index=True,
    )

    resource_type = models.CharField(
        max_length=100,
        blank=True,
    )

    resource_id = models.CharField(
        max_length=100,
        blank=True,
    )

    description = models.TextField()

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "-created_at"]
            ),
            models.Index(
                fields=["action", "-created_at"]
            ),
            models.Index(
                fields=[
                    "resource_type",
                    "resource_id",
                ]
            ),
        ]

    def __str__(self):
        username = (
            self.user.username
            if self.user
            else "system"
        )

        return (
            f"{username} | "
            f"{self.action} | "
            f"{self.resource_type} | "
            f"{self.resource_id}"
        )