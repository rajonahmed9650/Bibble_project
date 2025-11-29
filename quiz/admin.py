from django.contrib import admin
from .models import DailyQuiz,QuizAnswerOption,QuizAnswer
# Register your models here.


admin.site.register(DailyQuiz)
admin.site.register(QuizAnswerOption)
admin.site.register(QuizAnswer)