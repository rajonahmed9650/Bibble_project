from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        noti = Notification.objects.filter(user=user)
        serializer = NotificationSerializer(noti, many=True)
        return Response(serializer.data)


class MarkNotificationRead(APIView):
    def post(self, request, notification_id):
        user = request.user

        try:
            note = Notification.objects.get(id=notification_id, user=user)
        except Notification.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        # Mark read
        note.is_read = True
        note.save()

        # DELETE automatically
        note.delete()

        return Response({"message": "Notification marked read and deleted"})

