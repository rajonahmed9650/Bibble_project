from django.urls import path
from .views import (
    DailyQuizListCreate,
    DailyQuizDetail,
    QuizOptionListCreate,
   MultipleSubmitQuizAnswer,
)

urlpatterns = [
    path("",DailyQuizListCreate.as_view()),
    path("<int:pk>/",DailyQuizDetail.as_view()),

    path("quiz_option/",QuizOptionListCreate.as_view()),
    path("quiz_submit/",MultipleSubmitQuizAnswer.as_view()),
    # path("today_quiz/",TodayquizView.as_view()),

]