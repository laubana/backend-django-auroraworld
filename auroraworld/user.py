from rest_framework.decorators import api_view
from rest_framework.response import Response

from auroraworld.models import User
from auroraworld.verifyToken import verify_token


@verify_token
@api_view(['GET'])
def get_users(request):
    try:
        session_user_id = getattr(request, 'user_id', None)
        session_user_email = getattr(request, 'user_email', None)

        if not session_user_id or not session_user_email:
            return Response({'message': 'Unauthorized'}, status=401)

        existing_users = User.objects.exclude(id=session_user_id)

        return Response({'message': '', 'data': [
            {
                'id': existing_user.id,
                'email': existing_user.email,
            }
            for existing_user in existing_users
        ]}, status=200)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)
