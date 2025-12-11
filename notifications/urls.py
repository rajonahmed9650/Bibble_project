from django.urls import path
from .views import TestNotificationView

urlpatterns = [
    path("test-notif/", TestNotificationView.as_view()),   # ← FIXED
]

