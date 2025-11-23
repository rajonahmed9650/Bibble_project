from django.urls import path
from .views import*


urlpatterns = [
   path("auth/singup/",SignupView.as_view(),name="auth_singup"),
   path("auth/login/",LoginView.as_view(),name="auth_login"),
   # path("auth/otp/request/",OTPRequestView.as_view(),name=("auth_otp_request")),
   path("auth/otp/verify/",OTPVerifiyView.as_view(),name="auth_otp_verify"),
   path("forgot/password/", ForgotPasswordView.as_view(), name="forgot-password"),
   path("reset/password/", ResetPasswordView.as_view(), name="reset-password"),
   path("change/", ChangePasswordView.as_view(), name="change-password"),


]