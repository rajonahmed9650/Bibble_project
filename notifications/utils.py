

from .models import Notification

def create_notification(user, title, message, n_type):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=n_type
    )
