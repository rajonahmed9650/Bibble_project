
from django.urls import path
from .views import TodayStepView,CompleteDayView,UserProgressDaysView,CompleteDayItemView,allstepviews


urlpatterns = [
    path("today/<str:step>", TodayStepView.as_view()),
    path("complete-day/", CompleteDayView.as_view()),
    path("journey/<int:journey_id>/",UserProgressDaysView.as_view()),
    path("stepcopmplete/",CompleteDayItemView.as_view()),
    path("steps/<int:journey_id>/<int:day_id>", allstepviews.as_view()),

]