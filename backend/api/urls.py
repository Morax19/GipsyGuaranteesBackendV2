from .views import *
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    """
    User's paths and endpoints
    """
    # User registration
    path('userRegistration/', SubmitRegistrationView.as_view(), name='user_register'),
    # User login
    path('userLogin/', UserLoginView.as_view(), name='user_login'),
    # User Warranty Registration
    path('userWarrantyRegistration/', WarrantyRegistrationView.as_view(), name='warranty_register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registerWarranty/', register_warranty, name='register_warranty'),
    path('healthz/', healthz),
]
