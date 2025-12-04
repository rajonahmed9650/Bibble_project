from django.contrib import admin
from .models import DailyQuiz,QuizAnswerOption,QuizAnswer
# Register your models here.

class QuizAnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("id","option",)
    ordering = ("id",)

admin.site.register(DailyQuiz)
admin.site.register(QuizAnswerOption,QuizAnswerOptionAdmin)
admin.site.register(QuizAnswer)