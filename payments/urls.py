from django.urls import path
from .views import*

urlpatterns = [
    path("pay/",CreateCheckoutSession.as_view()),
    path("success/",CreateCheckoutSession.as_view()),
    path("cancel/",CreateCheckoutSession.as_view()),

]