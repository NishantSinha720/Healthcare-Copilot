from django.utils import timezone

from .models import AuditLog


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def create_audit_log(
    *,
    user=None,
    action,
    resource_type="",
    resource_id=None,
    description="",
    request=None,
    ip_address=None,
    metadata=None,
):
    if request is not None and ip_address is None:
        ip_address = get_client_ip(request)

    return AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=ip_address,
        metadata=metadata or {},
        created_at=timezone.now(),
    )