# notifications/urls.py
from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationReadView,
    ClearAllNotificationsView,
    NotificationListView,
    
)

urlpatterns = [
    path("", NotificationListView.as_view()),
    path("<int:pk>/read/", MarkNotificationReadView.as_view()),
    path("clear/", ClearAllNotificationsView.as_view()),

]
