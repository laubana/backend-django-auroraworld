from functools import wraps

import jwt
from django.conf import settings
from rest_framework.response import Response


def verify_token(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'message': 'Unauthorized'}, status=401)

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token,
                settings.ACCESS_TOKEN_SECRET,
                algorithms=['HS256']
            )
            request.user_id = payload.get('id')
            request.user_email = payload.get('email')
        except jwt.ExpiredSignatureError:
            return Response({'message': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'message': 'Invalid token'}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper
