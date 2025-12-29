from notifications.utils import create_notification
from django.utils import timezone
from userprogress.models import UserDayProgress
from .models import Notification
STAGE_LABEL = {
    "prayer": "Prayer",
    "devotion": "Devotion",
    "quiz": "Quiz",
    "action": "Action",
    "reflection": "Reflection",
}

# -------------------------
# Morning Summary
# -------------------------
def morning_journey_status():
    print("triggering;")
    

    today = timezone.localdate()

    current_days = UserDayProgress.objects.filter(status="current")
  

    for dp in current_days:
        user = dp.user
        day = dp.day_id


        #  same day duplicate prevent
        already_sent = Notification.objects.filter(
            user=user,
            notification_type="daily",
            created_at__date=today,
            title__icontains="Today is Day"
        ).exists()

        if already_sent:
            
            continue

        create_notification(
            user=user,
            title="Today's Journey",
            message=f"Today is Day {day.order}: {day.name}",
            n_type="daily"
        )
    

# -------------------------
# Prayer
# -------------------------


