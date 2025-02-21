from functools import wraps

import jwt
from django.conf import settings
from rest_framework.response import Response


def verify_token(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'message': 'Unauthorized'}, status=401)

            access_token_secret = settings.ACCESS_TOKEN_SECRET

            if not access_token_secret:
                return Response({'message': 'Unauthorized'}, status=401)

            token = auth_header.split(" ")[1]
            result = jwt.decode(
                token,
                access_token_secret,
                algorithms=['HS256']
            )

            user_id = result.get('id').strip()
            email = result.get('email').strip()

            if not user_id or not email:
                return Response({'message': 'Unauthorized'}, status=401)

            request.user_id = user_id
            request.user_email = email
        except Exception as error:
            print(error)

            return Response({'message': 'Server Error'}, status=500)
        return view_func(request, *args, **kwargs)

    return wrapper
