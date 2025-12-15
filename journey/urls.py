from django.urls import path
from .views import (
    JourneyListCreateAPIView,
    SingleJourneyAPIview,
    JourneyDetailsListCreateAPIView,
    JourneyDetailsAPIView, DayListCreateAPIView,
    DaysAPIView,
    JourneyIconListView,
    JourneyIconAPiView,
    UserJourneySequenceView,
    
 
    )


urlpatterns = [
    path("",JourneyListCreateAPIView.as_view()),
    path("<int:pk>/",SingleJourneyAPIview.as_view()),
    # path("currentjourney/",JourneyView.as_view()),


    path("details/",JourneyDetailsListCreateAPIView.as_view()),
    path("details/<int:pk>/",JourneyDetailsAPIView.as_view()),


    path("days/",DayListCreateAPIView.as_view()),
    path("days/<int:pk>/",DaysAPIView.as_view()),


    path("icon/",JourneyIconListView.as_view()),
    path("icon/<int:pk>/",JourneyIconAPiView.as_view()),
   
    path("all_journy/",UserJourneySequenceView.as_view()),

]