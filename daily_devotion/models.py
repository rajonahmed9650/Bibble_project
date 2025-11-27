from django.db import models
from journey.models import Journey,Days

# Create your models here.
class Daily_Devotion(models.Model):
    journey_id = models.ForeignKey(Journey,on_delete=models.CASCADE)
    days_id = models.ForeignKey(Days,on_delete=models.CASCADE)
    name = models.CharField(max_length=201)
    devotion = models.TextField(max_length=255)
    refiection = models.CharField(max_length=30)
    
    created_at = models.DateTimeField(auto_now_add=True)
    upatated_at = models.DateTimeField(auto_now=True)


class Daily_Prayer(models.Model):
    journey_id = models.ForeignKey(Journey,on_delete=models.CASCADE)
    days_id = models.ForeignKey(Days,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    prayer = models.TextField(max_length=255)
    audio = models.AutoField()

    created_at = models.DateTimeField(auto_now_add=True)
    upeated_at = models.DateTimeField(auto_now=True)    
    

class Micro_action(models.Model):
    journey_id = models.ForeignKey(Journey,on_delete=models.CASCADE)
    days_id = models.ForeignKey(Days,on_delete=models.CASCADE)
    action = models.CharField(max_length=255)    


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)