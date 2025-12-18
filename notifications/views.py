from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer



class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        updated = Notification.objects.filter(
            id=pk,
            user=request.user,
            is_read=False
        ).update(is_read=True)

        if updated == 0:
            return Response(
                {"message": "Already read or not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Notification marked as read"},
            status=status.HTTP_200_OK
        )


class ClearAllNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            "message": "All notifications marked as read",
            "updated": count
        })






# notifications/views.py

from django.utils import timezone
from datetime import timedelta


class NotificationListView(APIView):
    def get(self, request):
        user = request.user
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        qs = Notification.objects.filter(user=user)

        def serialize(qs):
            return [{
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "time": n.created_at.strftime("%I:%M %p")
            } for n in qs]

        return Response({
            "today": serialize(qs.filter(created_at__date=today)),
            "yesterday": serialize(qs.filter(created_at__date=yesterday)),
        })