from django.db import models
from journey.models import Journey, Days
from accounts.models import User

class DailyDevotion(models.Model):
    journey_id = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    scripture_name = models.CharField()
    devotion = models.TextField()
    reflection = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.scripture_name
    
    
class DailyReflectionSpace(models.Model):
    dailydevotion_id = models.ForeignKey(DailyDevotion,on_delete=models.CASCADE)
    reflection_note = models.TextField(blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reflection for {self.dailydevotion_id}"
    

    

class DailyPrayer(models.Model):
    journey_id = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    prayer = models.TextField()
    audio = models.FileField(upload_to="prayers/audio/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.day_id.name


class MicroAction(models.Model):
    journey_id = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    action = models.CharField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.action
