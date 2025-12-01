from django.db import models
from journey.models import Journey, Days
from accounts.models import User


class DailyQuiz(models.Model):
    journey_id= models.ForeignKey(Journey, on_delete=models.CASCADE)
    days_id = models.ForeignKey(Days, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question}-{self.id}"


class QuizAnswerOption(models.Model):
    daily_quiz = models.ForeignKey(DailyQuiz, on_delete=models.CASCADE, related_name="options")
    option = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.option}-{self.id}"
   

class QuizAnswer(models.Model):
    daily_quiz_id = models.ForeignKey(DailyQuiz,on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    quiz_answer_option_id = models.ForeignKey(QuizAnswerOption,on_delete=models.CASCADE)
    points = models.IntegerField()


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


