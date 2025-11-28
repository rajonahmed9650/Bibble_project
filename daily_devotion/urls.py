
from django.urls import path
from .views import DailyDevotionListCreate,DailDevotionDetails

urlpatterns = [
  path("",DailyDevotionListCreate.as_view(),),
  path("<int:pk>/",DailDevotionDetails.as_view()),
]   