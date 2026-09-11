from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.serializers import ModelSerializer

from .models import AuditLog


class AuditLogSerializer(ModelSerializer):
    class Meta:
        model = AuditLog
        fields = (
            "id",
            "user",
            "action",
            "resource_type",
            "resource_id",
            "description",
            "ip_address",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class AuditLogListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AuditLogSerializer

    queryset = AuditLog.objects.select_related(
        "user"
    ).all()