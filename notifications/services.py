from django.contrib.auth import get_user_model
from .models import Notification
from .utils import push_notification

User = get_user_model()

def send_daily_notification():
    users = User.objects.all()

    for user in users:
        notification = Notification.objects.create(
            user=user,
            title="Daily Reminder",
            message="It’s time for your daily prayer.",
            notification_type="daily"
        )

        # real-time push (if user online)
        push_notification(notification)
