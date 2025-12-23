from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
import os

from notifications.jobs import morning_journey_status


def start():
    """
    APScheduler start
   
    """

    #  Django auto-reload duplicate scheduler prevent
    if os.environ.get("RUN_MAIN") != "true":
        return

    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")


    scheduler.add_job(
        morning_journey_status,
        trigger=CronTrigger(minute="*/2"),  
        id="morning_journey_status",
        replace_existing=True,
    )

    scheduler.start()
   
