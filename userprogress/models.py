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
    completed_at = models.DateTimeField(null=True, blank=True) 

    class Meta:
        unique_together = ("user", "day_id")



# userprogress/models.py

from django.db import models
from django.contrib.auth import get_user_model
from journey.models import Days

User = get_user_model()


# ✅ ADD THIS MODEL (NEW)
class UserDayItemProgress(models.Model):
    ITEM_CHOICES = (
        ("prayer", "Daily Prayer"),
        ("devotion", "Daily Devotion"),
        ("action", "Today's Action"),
        ("reflection", "Reflection Space"),
        ("quiz", "Daily Quiz"),   # ✅ QUIZ ADDED
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.ForeignKey(Days, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20, choices=ITEM_CHOICES)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "day", "item_type")




class jourenystepitem(models.Model):

    ITEM_CHOICES = (
        ("prayer", "Daily Prayer"),
        ("devotion", "Daily Devotion"),
        ("action", "Today's Action"),
        ("reflection", "Reflection Space"),
      
    )

    journey_id = models.ForeignKey(Journey, on_delete=models.CASCADE)
    days_id = models.ForeignKey(Days, on_delete=models.CASCADE)

    step_name = models.CharField(max_length=20,choices=ITEM_CHOICES)

    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("days_id", "step_name")

