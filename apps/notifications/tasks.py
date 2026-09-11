from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from apps.accounts.models import User

from .models import Notification


@shared_task
def create_notification_task(
    user_id,
    notification_type,
    title,
    message,
):
    user = User.objects.get(
        id=user_id
    )

    notification = Notification.objects.create(
        recipient=user,
        notification_type=notification_type,
        title=title,
        message=message,
    )

    channel_layer = get_channel_layer()

    async_to_sync(
        channel_layer.group_send
    )(
        f"notifications_{user.id}",
        {
            "type": "notification_message",
            "data": {
                "id": notification.id,
                "notification_type": (
                    notification.notification_type
                ),
                "title": notification.title,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": (
                    notification.created_at.isoformat()
                ),
            },
        },
    )

    return {
        "notification_id": notification.id,
        "user_id": user.id,
    }