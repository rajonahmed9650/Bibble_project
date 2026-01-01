from django.urls import path
from .views import*

urlpatterns = [
    path("pay/",CreateCheckoutSession.as_view()),
    path("success/",CreateCheckoutSession.as_view()),
    path("cancel/",CreateCheckoutSession.as_view()),
    path("invoices/", MySubscriptionView.as_view()),
    path("currentplan/",CurrentPlanView.as_view()),
    path("currentplan/<int:id>/",CurrentPlanView.as_view()),
    
    path("invoices/<int:invoice_id>/pdf/",InvoicePDFView.as_view()),
    path("webhook/", StripeWebhook.as_view()),
]