import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"notifications_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        print("🔥 CONNECT:", self.group_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print("❌ DISCONNECT:", self.group_name)

    async def send_notification(self, event):
        print("🔥 EVENT RECEIVED:", event)

        response = {
            "title": event.get("title", ""),
            "message": event.get("message", ""),
            "notification_type": event.get("notification_type", "")
        }

        print("📤 SENDING:", response)
        await self.send(text_data=json.dumps(response))
