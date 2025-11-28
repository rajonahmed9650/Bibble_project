from django.db import models
from journey.models import Journey, Days


class DailyQuiz(models.Model):
    journey_id= models.ForeignKey(Journey, on_delete=models.CASCADE)
    days_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


class QuizAnswerOption(models.Model):
    daily_quiz = models.ForeignKey(DailyQuiz, on_delete=models.CASCADE, related_name="options")
    option = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.option
