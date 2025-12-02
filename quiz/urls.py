from django.urls import path
from .views import (
    DailyQuizListCreate,
    DailyQuizDetail,
    QuizOptionListCreate,
   
    SubmitQuizAnswer,
)





urlpatterns = [
    path("",DailyQuizListCreate.as_view()),
    path("<int:pk>/",DailyQuizDetail.as_view()),

    path("quiz_option/",QuizOptionListCreate.as_view()),
    path("quiz_submit/",SubmitQuizAnswer.as_view()),

]