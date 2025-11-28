from django.db import models
from journey.models import Journey, Days


class DailyDevotion(models.Model):
    journey_id = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    name = models.CharField(max_length=201)
    devotion = models.TextField(max_length=255)
    reflection = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DailyPrayer(models.Model):
    journey_id = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    prayer = models.TextField(max_length=255)
    audio = models.FileField(upload_to="prayers/audio/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MicroAction(models.Model):
    journey_id = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.action
