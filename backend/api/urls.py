from .views import *
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # User's paths and endpoints
    #   User Login
    #   User Registration
    #   User Change Password
    #   User Forgot Password
    #   User Warranty Registration
    path('userLogin/', UserLoginView.as_view(), name='user_login'),
    path('userRegistration/', SubmitRegistrationView.as_view(), name='user_register'),
    path('userChangePassword/', ChangePasswordView.as_view(), name='user_change_password'),
    path('userForgotPassword/', ForgotPasswordView.as_view(), name='user_forgot_password'),
    path('userWarrantyRegistration/', SubmitWarrantyView.as_view(), name='warranty_register'),


    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('healthz/', healthz),
]
