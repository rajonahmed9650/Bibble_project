# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]

        # 🔐 OPTIONAL security check (recommended)
        if self.scope["user"].is_authenticated:
            if self.scope["user"].id != self.user_id:
                await self.close()
                return

        self.group_name = f"notifications_{self.user_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "id": event.get("id"),
            "title": event.get("title"),
            "message": event.get("message"),
            "notification_type": event.get("notification_type"),
            "created_at": event.get("created_at"),
        }))
