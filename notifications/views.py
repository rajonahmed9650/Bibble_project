from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer



from django.utils import timezone

class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        is_read = request.data.get("is_read", True)

        Notification.objects.filter(
            id=pk,
            user=request.user
        ).update(is_read=is_read)

        return Response({"message": "Notification marked as read"})




class ClearAllNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        is_read = request.data.get("is_read", True)

        if is_read is not True:
            return Response(
                {"message": "Only is_read=true is allowed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            "success": True,
            "marked_read": updated,
            "message": "All notifications marked as read"
        }, status=status.HTTP_200_OK)





# notifications/views.py

from django.utils import timezone
from datetime import timedelta


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        qs = Notification.objects.filter(user=user)

        return Response({
            "today": NotificationSerializer(
                qs.filter(created_at__date=today),
                many=True
            ).data,

            "yesterday": NotificationSerializer(
                qs.filter(created_at__date=yesterday),
                many=True
            ).data,
            "unread_message": qs.filter(is_read=False).count(),
        })
