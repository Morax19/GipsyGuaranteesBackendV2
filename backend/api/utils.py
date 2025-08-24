import os
import jwt
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
            request.user_role = payload['role']
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return f(request, *args, **kwargs)