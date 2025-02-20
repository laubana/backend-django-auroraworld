import uuid

from django.db import IntegrityError
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Link, Category, Share
from .verifyToken import verify_token


@verify_token
@api_view(['POST'])
def add_link(request):
    try:
        category_id = request.data.get('categoryId').strip()
        name = request.data.get('name').strip()
        url = request.data.get('url').strip()

        if not category_id or not name or not url:
            return Response({'message': 'Invalid Input'}, status=400)

        session_user_id = getattr(request, 'user_id', None)
        session_user_email = getattr(request, 'user_email', None)

        if not session_user_id or not session_user_email:
            return Response({'message': 'Unauthorized'}, status=401)

        try:
            existing_category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'message': 'Invalid Input'}, status=400)

        new_link = None

        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                link_id = uuid.uuid4().hex

                new_link = Link.objects.create(
                    id=link_id,
                    user_id=session_user_id,
                    created_by=session_user_email,
                    category=existing_category,
                    category_name=existing_category.name,
                    name=name,
                    url=url,
                )

                break
            except IntegrityError as error:
                error_str = str(error).lower()

                if 'links.id' in error_str:
                    attempts += 1

                    continue
                else:
                    raise error

        if new_link:
            return Response({
                'message': 'Link created successfully.',
                'data': {
                    'id': new_link.id,
                    'user_id': new_link.user_id,
                    'created_by': new_link.created_by,
                    'category_id': new_link.category.id,
                    'category_name': new_link.category_name,
                    'name': new_link.name,
                    'url': new_link.url,
                },
            }, status=201)
        else:
            return Response({'message': 'No link created.'}, status=400)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)


@verify_token
@api_view(['GET'])
def get_links(request):
    try:
        mode = request.GET.get('mode').strip()
        category_id = request.GET.get('categoryId').strip()
        name = request.GET.get('name').strip()

        session_user_id = getattr(request, 'user_id', None)
        session_user_email = getattr(request, 'user_email', None)

        if not session_user_id or not session_user_email:
            return Response({'message': 'Unauthorized'}, status=401)

        if mode == 'own':
            existing_links = Link.objects.filter(user_id=session_user_id)
        elif mode == 'shared-unwritable':
            link_ids = Share.objects.filter(user_id=session_user_id, is_writable=False).values_list('link_id',
                                                                                                    flat=True)
            existing_links = Link.objects.filter(id__in=link_ids)
        else:
            link_ids = Share.objects.filter(user_id=session_user_id, is_writable=True).values_list('link_id', flat=True)

            existing_links = Link.objects.filter(id__in=link_ids)

        if category_id and category_id != 'all':
            existing_links = existing_links.filter(category_id=category_id)

        if name:
            existing_links = existing_links.filter(name__icontains=name)

        return Response({'message': '', 'data': [
            {
                'id': existing_link.id,
                'user_id': existing_link.user_id,
                'created_by': existing_link.created_by,
                'category_id': existing_link.category_id,
                'category_name': existing_link.category_name,
                'name': existing_link.name,
                'url': existing_link.url,
            }
            for existing_link in existing_links
        ]}, status=200)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)


@verify_token
@api_view(['DELETE', 'PUT'])
def remove_update_link(request, link_id):
    try:
        if request.method == 'DELETE':
            if not link_id:
                return Response({'message': 'Invalid Input'}, status=400)

            session_user_id = getattr(request, 'user_id', None)
            session_user_email = getattr(request, 'user_email', None)

            if not session_user_id or not session_user_email:
                return Response({'message': 'Unauthorized'}, status=401)

            deleted_link = Link.objects.filter(id=link_id, user_id=session_user_id).first()

            if not deleted_link:
                return Response({'message': 'No link removed.'}, status=400)

            deleted_count, _ = deleted_link.delete()

            if 0 < deleted_count:
                return Response({'message': 'Link removed successfully.'}, status=200)
            else:
                return Response({'message': 'No link removed.'}, status=400)
        elif request.method == 'PUT':
            category_id = request.data.get('categoryId').strip()
            name = request.data.get('name').strip()
            url = request.data.get('url').strip()

            if not link_id or not category_id or not name or not url:
                return Response({'message': 'Invalid Input'}, status=400)

            session_user_id = getattr(request, 'user_id', None)
            session_user_email = getattr(request, 'user_email', None)

            if not session_user_id or not session_user_email:
                return Response({'message': 'Unauthorized'}, status=401)

            try:
                existing_category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({'message': 'Invalid Input'}, status=400)

            updated_link = Link.objects.filter(id=link_id).filter(
                Q(user_id=session_user_id) | Q(share__user_id=session_user_id,
                                               share__is_writable=True)).distinct().first()

            if not updated_link:
                return Response({'message': 'No link updated.'}, status=400)

            updated_link.category = existing_category
            updated_link.category_name = existing_category.name
            updated_link.name = name
            updated_link.url = url
            updated_link.save()

            return Response({'message': 'Link updated successfully.', 'data': {
                'id': updated_link.id,
                'user_id': updated_link.user.id,
                'created_by': updated_link.created_by,
                'category_id': updated_link.category.id,
                'category_name': updated_link.category_name,
                'name': updated_link.name,
                'url': updated_link.url,
            }}, status=200)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)
