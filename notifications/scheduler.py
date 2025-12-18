# notifications/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore

from notifications.jobs import (
    morning_journey_status,
    prayer_notification,
    devotion_notification,
    quiz_notification,
    action_notification,
    reflection_notification,
)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        morning_journey_status,
        CronTrigger(hour=8, minute=5),
        id="morning",
        replace_existing=True,
    )

    scheduler.add_job(
        prayer_notification,
        CronTrigger(hour=8, minute=5),
        id="prayer",
        replace_existing=True,
    )

    scheduler.add_job(
        devotion_notification,
        CronTrigger(hour=8, minute=20),
        id="devotion",
        replace_existing=True,
    )

    scheduler.add_job(
        quiz_notification,
        CronTrigger(hour=8, minute=35),
        id="quiz",
        replace_existing=True,
    )

    scheduler.add_job(
        action_notification,
        CronTrigger(hour=8, minute=50),
        id="action",
        replace_existing=True,
    )

    scheduler.add_job(
        reflection_notification,
        CronTrigger(hour=9, minute=5),
        id="reflection",
        replace_existing=True,
    )

    scheduler.start()

