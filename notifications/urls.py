# notifications/urls.py
from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationReadView,
    ClearAllNotificationsView
)

urlpatterns = [
    path("", NotificationListView.as_view()),
    path("<int:pk>/read/", MarkNotificationReadView.as_view()),
    path("clear/", ClearAllNotificationsView.as_view()),
]
