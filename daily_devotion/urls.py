
from django.urls import path
from .views import (
    DailyDevotionListCreate,
    DailDevotionDetails,
    DailyPrayerListCreate,
    DailyPrayerDetail,
    MicroActionListCreate,
    MicroActionDetail,
   
    )

urlpatterns = [
  path("",DailyDevotionListCreate.as_view(),),
  path("<int:pk>/",DailDevotionDetails.as_view()),

  path("daily_prayer/",DailyPrayerListCreate.as_view()),
  path("daily_prayer/<int:pk>/",DailyPrayerDetail.as_view()),

  path("micro_action/",MicroActionListCreate.as_view()),
  path("micro_action/<int:pk>/",MicroActionDetail.as_view()),
]   