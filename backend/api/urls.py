from .views import *
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # User's paths and endpoints
    #   User Login
    #   User Registration
    #   User Change Password
    #   User Forgot Password
    #   User get Branches info
    #   User Warranty Registration
    path('userLogin/', UserLoginView.as_view(), name='user_login'),
    path('userRegistration/', SubmitRegistrationView.as_view(), name='user_register'),
    path('userEditProfile/', UserEditProfileView.as_view(), name='user_edit_profile'),
    path('userChangePassword/', ChangePasswordView.as_view(), name='user_change_password'),
    path('userForgotPassword/', ForgotPasswordView.as_view(), name='user_forgot_password'),
    path('userGetBranches/', GetBranchView.as_view(), name='user_get_branches'),
    path('userWarrantyRegistration/', SubmitWarrantyView.as_view(), name='warranty_register'),
    path('userWarrantyHistory/', UserWarrantyHistoryView.as_view(), name='warranty_history'),

    # Technical Services paths and endpoints
    #   Technical Services Login
    #   Technical Services Forgot Password
    path('technicalServicesLogin/', TechnicalServicesLoginView.as_view(), name='technical_services_login'),
    path('technicalServicesForgotPassword/', TechnicalServicesForgotPasswordView.as_view(), name='technical_services_forgot_password'),
    
    # Administration paths and endpoints
    #   Get Branch info
    #   Create Branch
    #   Edit Branch
    #   Get users info
    #   Create User
    #   Edit User
    path('getBranchAdmin/', GetBranchAdminView.as_view(), name='get_branch_admin'),
    path('createBranchAdmin/', CreateBranchAdminView.as_view(), name='create_branch_admin'),
    path('editBranchAdmin/', EditBranchAdminView.as_view(), name='edit_branch_admin'),
    path('getUsersAdmin/', GetUsersAdminView.as_view(), name='get_users_admin'),
    path('createUserAdmin/', CreateUserAdminView.as_view(), name='create_user_admin'),
    path('editUserAdmin/', EditUserAdminView.as_view(), name='edit_user_admin'),

    # Token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
