from django.urls import path
from .views import NotificationListView, MarkNotificationRead

urlpatterns = [
    path("", NotificationListView.as_view()),
    path("<int:pk>/read/", MarkNotificationRead.as_view()),
]
