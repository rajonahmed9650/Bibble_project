from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = NotificationSerializer(
            qs,
            many=True,
            context={"request": request}
        )

        return Response({
            "count": qs.count(),
            "notifications": serializer.data
        })



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
