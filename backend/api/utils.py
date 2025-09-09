import os
import jwt
import string
import secrets
from functools import wraps
from django.http import JsonResponse

def jwt_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)

        token = auth_header.split(' ')[1]
        jwt_secret = os.environ.get("JWT_SECRET_KEY")

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            request.user_id = payload['user_id']
            # Assuming you have a role in the token, as per your login view
            if 'role' in payload:
                request.user_role = payload['role'] 
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except KeyError as e:
            # Handle cases where a key like 'user_id' is missing from the payload
            return JsonResponse({'error': f'Invalid token payload: missing {e}'}, status=401)

        return f(request, *args, **kwargs) # <--- This line is critical!

    return decorated_function # <--- This line is also critical!

def generate_temp_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

