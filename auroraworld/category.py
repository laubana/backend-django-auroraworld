from rest_framework.decorators import api_view
from rest_framework.response import Response

from auroraworld.models import Category
from auroraworld.verifyToken import verify_token


@verify_token
@api_view(['GET'])
def get_categories(request):
    try:
        session_user_id = getattr(request, 'user_id', None)
        session_user_email = getattr(request, 'user_email', None)

        if not session_user_id or not session_user_email:
            return Response({'message': 'Unauthorized'}, status=401)

        existing_categories = Category.objects.all()

        return Response({'message': '', 'data': [
            {
                'id': existing_category.id,
                'name': existing_category.name,
            }
            for existing_category in existing_categories
        ]}, status=200)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)
