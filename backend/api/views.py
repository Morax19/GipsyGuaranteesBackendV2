import sys
import json
import secrets

from .models import Users, Warranty, WarrantyStatus

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.
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

def healthz(request):
    print("HEALTHZ Host header:", request.get_host(), file=sys.stderr)
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)

class SubmitWarrantyView(APIView):
    """
    API endpoint for user warranty registration.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        #   Role check
        if not hasattr(user, 'roleID') or user.roleID.roleName != 'Cliente':
            return Response({'error': 'Solo Clientes pueden registrar garantías'}, status=status.HTTP_403_FORBIDDEN)

        try:
            #   Extract warranty fields
            store_name = request.data.get('storeName')
            item_id = int(request.data.get('ItemId'))
            is_retail = request.data.get('isRetail') in ['true', 'True', True]
            purchase_date = request.data.get('purchaseDate')
            product_brand = request.data.get('productBrand')
            product_barcode = int(request.data.get('productBarcode'))
            invoice_path = request.data.get('invoiceCopyPath')

            # ✅ 3. Determine status
            # Example condition: warranty is available if purchase date is within 1 year and invoice is uploaded
            now = timezone.now().date()
            purchase_dt = timezone.datetime.strptime(purchase_date, "%Y-%m-%d").date()
            days_since_purchase = (now - purchase_dt).days

            if days_since_purchase <= 365 and invoice_path:
                status_code = "available"
                status_description = "Warranty is valid and invoice provided."
            else:
                status_code = "not available"
                status_description = "Warranty expired or invoice missing."

            # ✅ 4. Create WarrantyStatus
            status_obj = WarrantyStatus.objects.create(
                statusID=status_code,
                description=status_description
            )

            # ✅ 5. Create Warranty
            warranty = Warranty.objects.create(
                registerID=user,
                ItemId=item_id,
                isRetail=is_retail,
                purchaseDate=purchase_date,
                registrationDate=timezone.now(),
                statusID=status_obj,
                productBrand=product_brand,
                productBarcode=product_barcode,
                invoiceCopyPath=invoice_path
            )

            return Response({
                'message': 'Warranty registered.',
                'warrantyID': warranty.NroGarantia,
                'status': status_code,
                'reason': status_description
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_warranty(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    required_fields = ['username', 'product', 'serial_number', 'purchase_date']
    if not data or not all(field in data and data[field] for field in required_fields):
        return JsonResponse({'message': 'Missing required warranty fields'}, status=400)
    try:
        user = User.objects.get(username=data['username'])
    except User.DoesNotExist:
        return JsonResponse({'message': 'User does not exist'}, status=404)
    warranty = Warranty.objects.create(
        user=user,
        product=data['product'],
        serial_number=data['serial_number'],
        purchase_date=data['purchase_date']
    )
    return JsonResponse({'message': 'Warranty registered successfully!'}, status=201)


