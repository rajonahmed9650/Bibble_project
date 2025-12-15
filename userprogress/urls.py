
from django.urls import path
from .views import TodayView,CompleteDayView,UserProgressDaysView


urlpatterns = [
    path("today/", TodayView.as_view()),
    path("complete-day/", CompleteDayView.as_view()),
    path("journey/<int:journey_id>/",UserProgressDaysView.as_view()),

]