from django.core.management.base import BaseCommand
from notifications.scheduler import start
import time

class Command(BaseCommand):
    help = "Run notification scheduler"

    def handle(self, *args, **kwargs):
        start()
        while True:
            time.sleep(1)
