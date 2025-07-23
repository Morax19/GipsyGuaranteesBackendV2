from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Warranty
import json
from django.core.mail import send_mail
from django.conf import settings
import secrets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    return JsonResponse({
        "username": user.username,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_sudo": user.is_superuser,
    })

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return JsonResponse({'message': 'Missing username or password'}, status=400)
    user = authenticate(username=username, password=password)
    if user is not None:
        return JsonResponse({'message': f'User {username} logged in successfully!'})
    else:
        return JsonResponse({'message': 'Invalid credentials'}, status=401)

@csrf_exempt
@api_view(['POST'])
def submit_registration(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    required_fields = ['firstName', 'lastName', 'email', 'password']
    if not data or not all(field in data and data[field] for field in required_fields):
        return JsonResponse({'message': 'Missing required registration fields'}, status=400)
    # Check if user already exists by email
    if User.objects.filter(email=data['email']).exists():
        return JsonResponse({'message': 'User with this email already exists'}, status=400)
    # Create new user
    user = User.objects.create(
        username=data['email'],
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        password=make_password(data['password'])
    )
    return JsonResponse({'message': f"User {data['email']} registered successfully!"}, status=200)

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

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not username or not old_password or not new_password:
        return JsonResponse({'message': 'Missing required fields'}, status=400)
    user = authenticate(username=username, password=old_password)
    if user is None:
        return JsonResponse({'message': 'Invalid username or password'}, status=401)
    user.password = make_password(new_password)
    user.save()
    return JsonResponse({'message': 'Password changed successfully!'}, status=200)

@csrf_exempt
@require_POST
def forgot_password(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    email = data.get('email')
    if not email:
        return JsonResponse({'message': 'Missing email'}, status=400)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'message': 'No user with this email'}, status=404)
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
    return JsonResponse({'message': 'Temporary password sent to your email.'}, status=200)
