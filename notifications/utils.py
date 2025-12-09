from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification  # আপনার model থাকলে

def create_and_send_notification(user, title, message, notification_type="system"):
    # save in DB (optional)
    notif = Notification.objects.create(
        user=user, title=title, message=message, notification_type=notification_type
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.id}",
        {
            "type": "send_notification",  # maps to consumer method send_notification
            "id": notif.id,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "created_at": notif.created_at.isoformat(),
        }
    )
    return notif
