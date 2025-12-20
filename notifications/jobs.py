from notifications.utils import create_notification
from notifications.helpers import get_current_stage
from userprogress.models import UserDayProgress, UserDayItemProgress

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
from userprogress.models import UserDayProgress

from django.utils import timezone
from notifications.utils import create_notification
from userprogress.models import UserDayProgress
from .models import Notification

def morning_journey_status():
    print("🔔 Morning Day Notification running...")

    today = timezone.localdate()

    current_days = UserDayProgress.objects.filter(status="current")
    print(f"👉 Total current users: {current_days.count()}")

    for dp in current_days:
        user = dp.user
        day = dp.day_id
        print("--------------------------------------------------")
        print(f"👤 USER: {user.email}")
        print(f"📅 DAY: Day {day.order} - {day.name}")

        # ❌ same day duplicate prevent
        already_sent = Notification.objects.filter(
            user=user,
            notification_type="daily",
            created_at__date=today,
            title__icontains="Today is Day"
        ).exists()

        if already_sent:
            print("⚠️ Notification already sent today — SKIP")
            continue

        create_notification(
            user=user,
            title="Today's Journey",
            message=f"Today is Day {day.order}: {day.name}",
            n_type="daily"
        )
        print("✅ NOTIFICATION SENT")
        print(f"   Title   : Today's Journey")
        print(f"   Message : Today is Day {day.order}: {day.name}")

# -------------------------
# Prayer
# -------------------------


