
from django.urls import path
from .views import TodayView,CompleteDayView,UserProgressDaysView


urlpatterns = [
    path("today/", TodayView.as_view()),
    path("complete-day/", CompleteDayView.as_view()),
    path("current-journey/days/", UserProgressDaysView.as_view(), name="current_journey_days"),
]