# userprogress/models.py
from django.db import models
from django.contrib.auth import get_user_model
from journey.models import Journey, Days

User = get_user_model()


class UserJourneyProgress(models.Model):
    STATUS_CHOICES = (
        ("locked", "Locked"),
        ("current", "Current"),
        ("completed", "Completed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)

    completed_days = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="locked")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "journey")


class UserDayProgress(models.Model):
    STATUS_CHOICES = (
        ("locked", "Locked"),
        ("current", "Current"),
        ("completed", "Completed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="locked")

    class Meta:
        unique_together = ("user", "day_id")
