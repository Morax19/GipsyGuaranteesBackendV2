import sys
import json
import secrets

from .models import *

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny

# Admin API Views
#   Branch Management
class GetBranchAdminView(APIView):
    """
    API endpoint to get all branches and their related MainCustomer info for admin view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.roleID.description == 'Administrador':
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        branches = Branch.objects.select_related('customerID').all()
        result = []
        for branch in branches:
            branch_data = {
                'branchID': branch.branchID,
                'isRetail': branch.isRetail,
                'RIFtype': branch.RIFtype,
                'RIF': branch.RIF,
                'companyName': branch.companyName,
                'address': branch.address,
                'branchDescription': branch.branchDescription,
            }
            customer = branch.customerID
            customer_data = {
                'ID': customer.ID,
                'Company': customer.Company
            }
            branch_data['MainCustomer'] = customer_data
            result.append(branch_data)
        return Response(result, status=status.HTTP_200_OK)

class CreateBranchAdminView(APIView):
    """
    API endpoint for admin to create a new branch.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.roleID.description == 'Administrador':
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        required_fields = ['customerID', 'isRetail', 'RIFtype', 'RIF', 'companyName', 'address', 'branchDescription']
        if not data or not all(field in data and data[field] is not None for field in required_fields):
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate customerID exists
        try:
            customer = MainCustomer.objects.get(ID=data['customerID'])
        except MainCustomer.DoesNotExist:
            return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        branch = Branch.objects.create(
            customerID=customer,
            isRetail=data['isRetail'],
            RIFtype=data['RIFtype'],
            RIF=data['RIF'],
            companyName=data['companyName'],
            address=data['address'],
            branchDescription=data['branchDescription']
        )
        return Response({'message': 'Branch created successfully!', 'branchID': branch.branchID}, status=status.HTTP_201_CREATED)

class EditBranchAdminView(APIView):
    """
    API endpoint for admin to edit an existing branch.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.roleID.description == 'Administrador':
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        required_fields = ['branchID', 'customerID', 'isRetail', 'RIFtype', 'RIF', 'companyName', 'address', 'branchDescription']
        if not data or not all(field in data and data[field] is not None for field in required_fields):
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate branch exists
        try:
            branch = Branch.objects.get(branchID=data['branchID'])
        except Branch.DoesNotExist:
            return Response({'message': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate customerID exists
        try:
            customer = MainCustomer.objects.get(ID=data['customerID'])
        except MainCustomer.DoesNotExist:
            return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        branch.customerID = customer
        branch.isRetail = data['isRetail']
        branch.RIFtype = data['RIFtype']
        branch.RIF = data['RIF']
        branch.companyName = data['companyName']
        branch.address = data['address']
        branch.branchDescription = data['branchDescription']
        branch.save()
        return Response({'message': 'Branch updated successfully!'}, status=status.HTTP_200_OK)
    
#   User Management
class UserEditProfileView(APIView):
    """
    API endpoint for users to edit their profile information.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        required_fields = ['firstName', 'lastName', 'email', 'address']
        if not data or not all(field in data and data[field] is not None for field in required_fields):
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        # Update user fields
        user.User = data['email']
        user.email = data['email']
        # Update related customer info if exists
        if hasattr(user, 'CustomerID') and user.CustomerID:
            customer = user.CustomerID
            customer.FirstName = data['firstName']
            customer.LastName = data['lastName']
            customer.Address = data['address']
            customer.EmailAddress = data['email']
            customer.save()
        user.save()
        return Response({'message': 'Profile updated successfully!'}, status=status.HTTP_200_OK)

class GetUsersAdminView(APIView):
    """
    API endpoint to get all users for admin view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Optionally restrict to admin users only
        if not request.user.roleID.description == 'Administrador':
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        users = Users.getUsersAdmin()
        return Response(users, status=status.HTTP_200_OK)

class CreateUserAdminView(APIView):
    """
    API endpoint for admin to create a new user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Optionally restrict to admin users only
        if not request.user.roleID.description == 'Administrador':
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        required_fields = ['username', 'password', 'customRegDate', 'roleIDDescription']

        if not data or not all(field in data and data[field] for field in required_fields):
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists by email
        if Users.objects.filter(username=data['username']).exists():
            return Response({'message': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user
        if data['roleIDDescription'] == 'Administrador':
            role = Users.Role.objects.get(roleName='Administrador')
            user = Users.objects.create_admin(
                username=data['username'],
                password=make_password(data['password']),
                registrationDate=data['customRegDate'],
                roleID=role
            )
        elif data['roleIDDescription'] == 'Servicio Tecnico':
            role = Users.Role.objects.get(roleName='Servicio Tecnico')
            user = Users.objects.create_technical_service(
                username=data['username'],
                password=make_password(data['password']),
                registrationDate=data['customRegDate'],
                roleID=role
            )
        else:
            return Response({'message': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': f"User {data['email']} created successfully!"}, status=status.HTTP_201_CREATED)
    
class EditUserAdminView(APIView):
    """
    API endpoint for admin to edit an existing user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only allow admins to edit users
        if not request.user.roleID.description == 'Administrador':
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        required_fields = ['username', 'password', 'customRegDate', 'roleIDDescription']

        if not data or not all(field in data and data[field] for field in required_fields):
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(username=data['username'])
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update user fields
        user.set_password(data['password'])
        user.registrationDate = data['registrationDate']
        # Find the role by description
        try:
            role = Role.objects.get(description=data['roleIDDescription'])
        except Role.DoesNotExist:
            return Response({'message': 'Invalid role description'}, status=status.HTTP_400_BAD_REQUEST)
        user.roleID = role
        user.save()
        return Response({'message': 'User updated successfully!'}, status=status.HTTP_200_OK)

#   User API Views
class SubmitRegistrationView(APIView):
    """
    API endpoint for user registration.
    """
    permission_classes = [AllowAny]

    def post(self, request): 
        data = request.data
        required_fields = ['firstName', 'lastName', 'email', 'password']
        
        if not data or not all(field in data and data[field] for field in required_fields):
            return Response({'message': 'Missing required registration fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists by email
        if Users.objects.filter(email=data['email']).exists():
            return Response({'message': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user
        user = Users.objects.create_customer(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            password=make_password(data['password']),
            address=data.get('address'),
            phone=data.get('phone'),
            zip_code=data.get('zip_code')
        )

        return Response({'message': f"User {data['email']} registered successfully!"}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    """
    API endpoint for user login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception:
            return Response({'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response({'message': 'Missing username or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'userID': user.userID,
                    'username': user.Users,
                    'role': user.roleID.Description,
                    'is_staff': user.is_staff,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CurrentUserView(APIView):
    """
    Returns the authenticated user's information
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        user_info = {
            "username": user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }

        return Response(user_info, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    """
    API endpoint for users to change their password
    """
    def post(self, request):
        user = request.user
        data = request.data

        current_password = data.get('oldPassword')
        new_password = data.get('newPassword')

        if not current_password or not new_password:
            return Response({'message': 'Missing oldPassword or newPassword'}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(current_password, user.password):
            return Response({'message': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        if current_password == new_password:
            return Response({'message': 'New password cannot be the same as the old password'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.save()

        return Response({'message': 'Password changed successfully!'}, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    """
    API endpoint for users to reset their password
    """
    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'message': 'Missing email'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response({'message': 'No user with this email'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a temporary password
        temp_password = secrets.token_urlsafe(8)
        user.password = make_password(temp_password)
        user.save()

        # Send email with the temporary password
        send_mail(
            'Password Reset',
            f'Your temporary password is: {temp_password}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

        return Response({'message': 'Temporary password sent to your email.'}, status=status.HTTP_200_OK)

class GetBranchView(APIView):
    """
    API endpoint to get all branches with id, name, and address for select tags.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        branches = Branch.objects.all().values('branchID', 'companyName', 'address')
        return Response(list(branches), status=status.HTTP_200_OK)

class SubmitWarrantyView(APIView):
    """
    API endpoint for users to register a new warranty (with file upload).
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data
        required_fields = [
            'branchID', 'purchaseDate', 'invoiceNumber', 'productBrand',
            'productModel', 'productBarcode', 'invoiceFile'
        ]
        if not data or not all(field in data and data[field] is not None for field in required_fields):
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate branch exists
        try:
            branch = Branch.objects.get(branchID=data['branchID'])
        except Branch.DoesNotExist:
            return Response({'message': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)

        # Handle file upload
        invoice_file = request.FILES.get('invoiceFile')
        if not invoice_file:
            return Response({'message': 'Invoice file is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Save file to media directory (or handle as needed)
        from django.core.files.storage import default_storage
        file_path = default_storage.save(f'invoices/{invoice_file.name}', invoice_file)

        # Ensure default statuses exist and get correct status based on purchaseDate
        status = WarrantyStatus.create_default_statuses(purchaseDate=data['purchaseDate'])
        if not status:
            return Response({'message': 'Could not set warranty status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        warranty = Warranty.objects.create(
            registerID=request.user,
            branchID=branch,
            ItemId=data.get('invoiceNumber'),
            isRetail=branch.isRetail,
            purchaseDate=data['purchaseDate'],
            registrationDate=timezone.now().date(),
            statusID=status,
            productBrand=data['productBrand'],
            productBarcode=data['productBarcode'],
            invoiceCopyPath=file_path
        )
        return Response({'message': 'Warranty registered successfully!', 'NroGarantia': warranty.NroGarantia}, status=status.HTTP_201_CREATED)

class UserWarrantyHistoryView(APIView):
    """
    API endpoint to get all warranties registered by a given client (user).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'message': 'Missing user_id parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(id_user=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        warranties = Warranty.objects.filter(registerID=user)
        result = []
        for warranty in warranties:
            result.append({
                'NroGarantia': warranty.NroGarantia,
                'branchID': warranty.branchID.branchID,
                'branchName': warranty.branchID.companyName,
                'ItemId': warranty.ItemId,
                'isRetail': warranty.isRetail,
                'purchaseDate': warranty.purchaseDate,
                'registrationDate': warranty.registrationDate,
                'statusID': warranty.statusID.statusID,
                'statusDescription': warranty.statusID.description,
                'productBrand': warranty.productBrand,
                'productBarcode': warranty.productBarcode,
                'invoiceCopyPath': warranty.invoiceCopyPath
            })
        return Response(result, status=status.HTTP_200_OK)

class TechnicalServicesLoginView(APIView):
    """
    API endpoint for technical services login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception:
            return Response({'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response({'message': 'Missing username or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None and user.roleID.roleName == 'Servicio Tecnico':
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'userID': user.userID,
                    'username': user.Users,
                    'role': user.roleID.Description,
                    'is_staff': user.is_staff,
                }
            }, status=status.HTTP_200_OK)
    
class TechnicalServicesForgotPasswordView(APIView):
    """
    API endpoint for technical services to reset their password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'message': 'Missing email'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(email=email, roleID__roleName='Servicio Tecnico')
        except Users.DoesNotExist:
            return Response({'message': 'No user with this email'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a temporary password
        temp_password = secrets.token_urlsafe(8)
        user.password = make_password(temp_password)
        user.save()

        # Send email with the temporary password
        send_mail(
            'Password Reset',
            f'Your temporary password is: {temp_password}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True,
        )

        return Response({'message': 'Temporary password sent to your email.'}, status=status.HTTP_200_OK)

class TechnicalServicesWarrantyView(APIView):
    """
    API endpoint to get all info of a Warranty given its WarrantyID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, warranty_id):
        if not warranty_id:
            return Response({'message': 'Missing warranty_id parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            warranty = Warranty.objects.get(NroGarantia=warranty_id)
        except Warranty.DoesNotExist:
            return Response({'message': 'Warranty not found'}, status=status.HTTP_404_NOT_FOUND)

        result = {
            'NroGarantia': warranty.NroGarantia,
            'registerID': warranty.registerID.id_user if hasattr(warranty.registerID, 'id_user') else None,
            'branchID': warranty.branchID.branchID if hasattr(warranty.branchID, 'branchID') else None,
            'branchName': warranty.branchID.companyName if hasattr(warranty.branchID, 'companyName') else None,
            'ItemId': warranty.ItemId,
            'isRetail': warranty.isRetail,
            'purchaseDate': warranty.purchaseDate,
            'registrationDate': warranty.registrationDate,
            'statusID': warranty.statusID.statusID if hasattr(warranty.statusID, 'statusID') else None,
            'statusDescription': warranty.statusID.description if hasattr(warranty.statusID, 'description') else None,
            'productBrand': warranty.productBrand,
            'productBarcode': warranty.productBarcode,
            'invoiceCopyPath': warranty.invoiceCopyPath
        }
        return Response(result, status=status.HTTP_200_OK)