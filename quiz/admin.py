from django.contrib import admin
from .models import DailyQuiz,QuizAnswerOption,QuizAnswer
# Register your models here.

class QuizAnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("id","option",)
    ordering = ("id",)

admin.site.register(QuizAnswerOption,QuizAnswerOptionAdmin)
class DaliyQuizAdmin(admin.ModelAdmin):
    list_display = ("id","question")
    ordering = ("id",)
admin.site.register(DailyQuiz,DaliyQuizAdmin)



admin.site.register(QuizAnswer)