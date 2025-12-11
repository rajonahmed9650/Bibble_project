from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_ws_notification(user_id, title, message, notification_type="system"):
    print("🔥 send_ws_notification CALLED for user:", user_id)

    channel_layer = get_channel_layer()
    print("→ Channel Layer:", channel_layer)

    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",
        {
            "type": "send_notification",
            "title": title,
            "message": message,
            "notification_type": notification_type,
        }
    )

    print("🔥 Notification SENT → Group:", f"notifications_{user_id}")
