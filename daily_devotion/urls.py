
from django.urls import path
from .views import (
    DailyDevotionListCreate,
    DailDevotionDetails,
    DailyPrayerListCreate,
    DailyPrayerDetail,
    MicroActionListCreate,
    MicroActionDetail,
    DailyReflectionSpace,


    TodayDevotionView,
    TodayPrayerView,
    TodayMicroActionView
   
    )

urlpatterns = [
  path("",DailyDevotionListCreate.as_view(),),
  path("<int:pk>/",DailDevotionDetails.as_view()),

  path("daily_prayer/",DailyPrayerListCreate.as_view()),
  path("daily_prayer/<int:pk>/",DailyPrayerDetail.as_view()),
  path("reflection_note/",DailyReflectionSpace.as_view()),

  path("micro_action/",MicroActionListCreate.as_view()),
  path("micro_action/<int:pk>/",MicroActionDetail.as_view()),



  path("today/devotion/", TodayDevotionView.as_view()),
  path("today/prayer/",TodayPrayerView.as_view()),
  path("today/action/",TodayMicroActionView.as_view()),
]   