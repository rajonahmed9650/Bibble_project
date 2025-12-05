from django.db import models
from django.contrib.auth import get_user_model
from journey.models import Journey, Days

User = get_user_model()

class UserJourneyProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)

    completed_days = models.PositiveIntegerField(default=0)  # কত দিন শেষ করেছে
    completed = models.BooleanField(default=False)           # পুরো journey শেষ?

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "journey")

    def __str__(self):
        return f"{self.user.email} → {self.journey.name} ({self.completed_days}/7)"



class UserDayProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_id = models.ForeignKey(Days, on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} → Day {self.day_id.order} of {self.day_id.journey_id.name}"
