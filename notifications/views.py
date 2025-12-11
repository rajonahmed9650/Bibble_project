from rest_framework.views import APIView
from rest_framework.response import Response
from .notification_sender import send_ws_notification

class TestNotificationView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        print("🔥 Trigger called for user:", user_id)

        send_ws_notification(
            user_id=user_id,
            title="Welcome!",
            message="Test notification working!",
            notification_type="test"
        )

        return Response({"status": "sent"})

