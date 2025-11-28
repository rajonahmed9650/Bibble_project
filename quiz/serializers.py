from rest_framework import serializers
from .models import DailyQuiz,QuizAnswerOption


class QuizAnswerOptionSer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswerOption
        fields = ["id","daily_quiz","option"]


class DailyQuizSerializer(serializers.ModelSerializer):
    options = QuizAnswerOptionSer(many = True,read_only = True)


    class Meta:
        model = DailyQuiz
        fields = ["id","journey_id","days_id","question"]        