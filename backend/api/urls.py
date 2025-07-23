from django.urls import path
from .views import submit_registration, register_warranty, change_password, forgot_password, current_user
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('submitRegistration/', submit_registration, name='submit_registration'),
    path('registerWarranty/', register_warranty, name='register_warranty'),
    path('changePassword/', change_password, name='change_password'),
    path('forgotPassword/', forgot_password, name='forgot_password'),
    path('current_user/', current_user, name='current_user'),
]
