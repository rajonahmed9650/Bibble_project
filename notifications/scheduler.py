from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from .services import send_daily_notification

_scheduler = None   # 🔐 global lock


def start():
    global _scheduler

    if _scheduler:
        return   # already started

    scheduler = BackgroundScheduler(timezone="Asia/Dhaka")
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        send_daily_notification,
        trigger="cron",
        hour=6,
        minute=0,
        id="daily_6am_notification",
        replace_existing=True,
    )

    scheduler.start()
    _scheduler = scheduler
