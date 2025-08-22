from .views import *
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# CSRF Test
@ensure_csrf_cookie
def test_csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

urlpatterns = [
    # User's paths and endpoints
    #   User Login
    #   User Registration
    #   User Change Password
    #   User Forgot Password
    #   User get Branches info
    #   User Warranty Registration
    path('userRegister/', userRegister, name='user_register'),

    # Technical Services paths and endpoints
    #   Technical Services Login
    #   Technical Services Forgot Password
    
    # Administration paths and endpoints
    #   Get all users
    #   Get all branches
    #   Get all customers
    #   Create user
    #   Edit user
    #   Create branch
    #   Edit branch
    #   Get all Main.Customers
    path('adminGetUsers/', adminGetUsers, name='admin_get_users'),
    path('adminGetBranches/', adminGetBranches, name='admin_get_branches'),
    path('adminGetCustomers/', adminGetCustomers, name='admin_get_customers'),
    path('adminCreateUser/', adminCreateUser, name='admin_create_user'),
    path('adminEditUser/', adminEditUser, name='admin_edit_user'),
    path('adminCreateBranch/', adminCreateBranch, name='admin_create_branch'),
    path('adminEditBranch/', adminEditBranch, name='admin_edit_branch'),
    path('adminGetMainCustomers/', adminGetMainCustomers, name='admin_get_MainCustomers'),
    
    # Token management
    path('token-getCSRFTest/', test_csrf, name='test_csrf'),
    path('token-getCSRF/', getCSRF, name='get_csrf_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
