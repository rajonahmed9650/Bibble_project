from django.urls import path
from .views import (
    SignupView,
    LoginView,
    OTPVerifiyView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    LogoutView,
    ProfileView,
    CategorizeView,
    DisableAccountView
    )


urlpatterns = [
   path("auth/signup/",SignupView.as_view(),name="auth_singup"),
   path("auth/login/",LoginView.as_view(),name="auth_login"),
   path("auth/otp/verify/",OTPVerifiyView.as_view(),name="auth_otp_verify"),
   path("forgot/password/", ForgotPasswordView.as_view(), name="forgot-password"),
   path("reset/password/", ResetPasswordView.as_view(), name="reset-password"),
   path("change/", ChangePasswordView.as_view(), name="change-password"),
   path("auth/logout/", LogoutView.as_view(), name="auth_logout"),
   path("profile/", ProfileView.as_view(), name="profile"),
   path("user_categorize/",CategorizeView.as_view(),name="category"),
   path("account/disable/", DisableAccountView.as_view()),

]