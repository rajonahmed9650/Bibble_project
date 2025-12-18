from notifications.utils import create_notification
from notifications.helpers import get_current_stage
from userprogress.models import UserJourneyProgress, UserDayItemProgress

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
    progresses = UserJourneyProgress.objects.filter(completed=False)

    for p in progresses:
        # ✅ এই user + এই journey এর current (incomplete) day
        day_item = (
            UserDayItemProgress.objects
            .filter(
                user=p.user,
                day__journey_id=p.journey,
                completed=False
            )
            .order_by("day__order")
            .first()
        )

        print("USER:", p.user)
        print("DAY ITEM:", day_item)

        if not day_item:
            continue

        day = day_item.day
        stage = get_current_stage(p.user, day)

        print("STAGE:", stage)

        if not stage:
            print("SKIP: No stage")
            continue
        print("CREATE NOTIFICATION NOW")

        create_notification(
            user=p.user,
            title="Your Journey Today",
            message=f"Day {day.order}: {day.name}\nCurrent focus: {STAGE_LABEL[stage]}",
            n_type="journey"
        )


# -------------------------
# Prayer
# -------------------------
def prayer_notification():
    for p in UserJourneyProgress.objects.filter(completed=False):
        create_notification(
            p.user,
            "Daily Prayer Reminder",
            "It's time for your morning prayer.",
            "prayer"
        )


# -------------------------
# Devotion
# -------------------------
def devotion_notification():
    for p in UserJourneyProgress.objects.filter(completed=False):
        create_notification(
            p.user,
            "Your Daily Devotion is ready",
            "Start your day with a moment of reflection.",
            "daily"
        )


# -------------------------
# Quiz
# -------------------------
def quiz_notification():
    for p in UserJourneyProgress.objects.filter(completed=False):
        create_notification(
            p.user,
            "Daily Quiz",
            "Answer today’s quiz question.",
            "system"
        )


# -------------------------
# Action
# -------------------------
def action_notification():
    for p in UserJourneyProgress.objects.filter(completed=False):
        create_notification(
            p.user,
            "Take Action",
            "Apply today’s lesson in your life.",
            "system"
        )


# -------------------------
# Reflection
# -------------------------
def reflection_notification():
    for p in UserJourneyProgress.objects.filter(completed=False):
        create_notification(
            p.user,
            "Reflection Time",
            "Spend a moment reflecting on today.",
            "system"
        )
