
from django.urls import path
from .views import TodayView,CompleteDayView


urlpatterns = [
    path("today/", TodayView.as_view()),
    path("complete-day/", CompleteDayView.as_view()),
]