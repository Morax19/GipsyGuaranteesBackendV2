from django.urls import path
from .views import (
    userLogin,
    publicRegister,
    warrantyRegister,
    warrantyHistory,
    userProfileEdit,
    userChangePassword,
    technicalServiceLogin,
    adminLogin,
    adminCreateUsers,
    adminEditUsers,
    adminCreateBranch,
    adminEditBranch,
    adminGetUsers,
    adminGetBranches,
    adminGetCustomerByID,
    adminGetMainCustomers,
    adminGetRoles,
    getBranchByCustomerID,
    adminGetMainCustomersRetail,
    getProductByBarCode,
    getCustomerByUserID,
    technicalServiceGetWarrantyByID,
    technicalServiceOpenCaseWarranty,
    technicalServiceUpdateCase,
    updateWarrantyUsedCount,
    technicalServiceHistory,
    technicalServiceGetStatus,
    technicalServiceGetIssue,
)


urlpatterns = [
    # User's paths and endpoints
    #   Login
    #   Public Register
    #   Warranty Register
    #   Warranty History
    #   Edit Profile
    #   User Change Password
    path('userLogin/', userLogin, name='user_login'),
    path('publicRegister/', publicRegister, name='user_register'),
    path('warrantyRegister/', warrantyRegister, name='warranty_register'),
    path('warrantyHistory/', warrantyHistory, name='warranty_history'),
    path('userProfileEdit/', userProfileEdit, name='user_profile_edit'),
    path('userChangePassword/', userChangePassword, name='user_change_password'),    

    # Technical Services paths and endpoints
    #   Login
    #   Forgot Password
    path('technicalServiceLogin/', technicalServiceLogin, name='technical_service_login'),
    path('technicalServiceGetWarrantyByID/', technicalServiceGetWarrantyByID, name='technical_service_get_warranty_by_id'),
    path('technicalServiceOpenCaseWarranty/', technicalServiceOpenCaseWarranty, name='technical_service_open_case_warranty'),
    path('technicalServiceUpdateCase/', technicalServiceUpdateCase, name='technical_service_update_case'),
    path('updateWarrantyUsedCount/', updateWarrantyUsedCount, name='update_warranty_used_count'),
    path('technicalServiceHistory/', technicalServiceHistory, name='technical_service_history'),
    path('technicalServiceGetStatus/', technicalServiceGetStatus, name='technical_service_get_status'),
    path('technicalServiceGetIssue/', technicalServiceGetIssue, name='technical_service_get_issue'),

    # Administration paths and endpoints
    #   Login
    #   Create Users
    #   Edit Users
    #   Create Branch
    #   Edit Branch
    path('adminLogin/', adminLogin, name='admin_login'),    
    path('adminCreateUsers/', adminCreateUsers, name='admin_create_users'),
    path('adminEditUsers/', adminEditUsers, name='admin_edit_users'),
    path('adminCreateBranch/', adminCreateBranch, name='admin_create_branch'),
    path('adminEditBranch/', adminEditBranch, name='admin_edit_branch'),

    #   Get all users
    #   Get all branches
    #   Get all customers
    #   Create user
    #   Edit user
    #   Create branch
    #   Edit branch
    #   Get all Main.Customers (With Warranty.Invetory)
    #   Get all roles
    path('adminGetUsers/', adminGetUsers, name='admin_get_users'),
    path('adminGetBranches/', adminGetBranches, name='admin_get_branches'),
    path('adminGetCustomerByID/', adminGetCustomerByID, name='admin_get_customer_by_id'),
    path('getCustomerByUserID/', getCustomerByUserID, name='get_customer_by_user_id'),
    path('adminGetMainCustomers/', adminGetMainCustomers, name='admin_get_MainCustomers'),
    path('adminGetMainCustomersRetail/', adminGetMainCustomersRetail, name='admin_get_MainCustomers_retail'),
    path('adminGetRoles/', adminGetRoles, name='admin_get_roles'),
    path('getBranchByCustomerID/', getBranchByCustomerID, name='get_branch_by_customer_id'),
    path('getProductByBarCode/', getProductByBarCode, name='get_product_by_barCode'),
]