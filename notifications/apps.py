# notifications/apps.py
from django.apps import AppConfig
import os

class NotificationsConfig(AppConfig):
    name = "notifications"

    def ready(self):
        # run scheduler only in main process
        if os.environ.get("RUN_MAIN") == "true":
            from .scheduler import start
            start()
