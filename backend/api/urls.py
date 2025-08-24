from .views import *
from django.urls import path

urlpatterns = [
    # General endpoints
    #   Registration
    #   Edit information
    #   Login
    path('userRegister/', userRegister, name='user_register'),
    path('userEdit/', userEdit, name='user_edit'),

    # User's paths and endpoints
    #   Login
    #   User Change Password
    #   User Forgot Password
    #   User get Branches info
    #   User Warranty Registration
    path('userLogin/', userLogin, name='user_login'),
    path('warrantyRegister/', warrantyRegister, name='warranty_register'),
    

    # Technical Services paths and endpoints
    #   Login
    #   Forgot Password
    path('technicalServiceLogin/', technicalServiceLogin, name='technical_service_login'),
    
    # Administration paths and endpoints
    #   Login
    #   Get all users
    #   Get all branches
    #   Get all customers
    #   Create user
    #   Edit user
    #   Create branch
    #   Edit branch
    #   Get all Main.Customers (With Warranty.Invetory)
    #   Get all roles
    path('adminLogin/', adminLogin, name='admin_login'),
    path('adminGetUsers/', adminGetUsers, name='admin_get_users'),
    path('adminGetBranches/', adminGetBranches, name='admin_get_branches'),
    path('adminGetCustomers/', adminGetCustomers, name='admin_get_customers'),
    path('adminCreateBranch/', adminCreateBranch, name='admin_create_branch'),
    path('adminEditBranch/', adminEditBranch, name='admin_edit_branch'),
    path('adminGetMainCustomers/', adminGetMainCustomers, name='admin_get_MainCustomers'),
    path('adminGetRoles/', adminGetRoles, name='admin_get_roles'),
]
