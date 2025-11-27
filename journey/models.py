from django.db import models

# Create your models here.
class Journey(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f"{self.name}-{self.id}"
    

class JourneyDetails(models.Model):
    journey_id = models.ForeignKey(Journey,on_delete=models.CASCADE , related_name="details")
    image = models.ImageField(upload_to="journey/details")
    details = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.journey_id.name} Details"
    

class Days(models.Model):
    journey_id = models.ForeignKey(Journey,on_delete=models.CASCADE,related_name='days')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="journey/days")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.journey_id.name}-{self.name}"


class Journey_icon(models.Model):
    journey_id = models.ForeignKey(Journey,on_delete=models.CASCADE,related_name="icons")
    icon = models.ImageField(upload_to="journey/icons")  

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  


    def __str__(self):
        return f"{self.journey_id.name} Icon"