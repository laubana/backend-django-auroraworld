import uuid

from django.db import IntegrityError, transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response

from auroraworld.models import Link, User, Share
from auroraworld.verifyToken import verify_token


@verify_token
@api_view(['POST'])
def add_share(request):
    try:
        share_id = request.data.get('linkId').strip()
        user_id = request.data.get('userId').strip()
        is_writable = request.data.get('isWritable')

        if not share_id or not user_id:
            return Response({'message': 'Invalid Input'}, status=400)

        session_user_id = getattr(request, 'user_id', None)
        session_user_email = getattr(request, 'user_email', None)

        if not session_user_id or not session_user_email:
            return Response({'message': 'Unauthorized'}, status=401)

        try:
            existing_link = Link.objects.get(id=share_id)
        except Link.DoesNotExist:
            return Response({'message': 'Invalid Input'}, status=400)

        try:
            existing_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'Invalid Input'}, status=400)

        new_share = None

        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                share_id = uuid.uuid4().hex

                new_share = Share.objects.create(
                    id=share_id,
                    link=existing_link,
                    user=existing_user,
                    user_email=existing_user.email,
                    is_writable=1 if is_writable else 0,
                )

                break
            except IntegrityError as error:
                error_str = str(error).lower()

                if 'shares.id' in error_str:
                    attempts += 1

                    continue
                else:
                    raise error

        if new_share is not None:
            return Response({
                'message': 'Share created successfully.',
                'data': {
                    'id': new_share.id,
                    'link_id': new_share.link_id,
                    'user_id': new_share.user_id,
                    'user_email': new_share.user_email,
                    'is_writable': new_share.is_writable,
                },
            }, status=201)
        else:
            return Response({'message': 'No share created.'}, status=400)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)


@verify_token
@api_view(['POST'])
def add_shares(request):
    try:
        link_ids = request.data.get('linkIds')
        user_ids = request.data.get('userIds')
        is_writable = request.data.get('isWritable')

        if not link_ids or not isinstance(link_ids, list) or len(link_ids) <= 0 \
                or not user_ids or not isinstance(user_ids, list) or len(user_ids) <= 0:
            return Response({'message': 'Invalid Input'}, status=400)

        session_user_id = getattr(request, 'user_id', None)
        session_user_email = getattr(request, 'user_email', None)

        if not session_user_id or not session_user_email:
            return Response({'message': 'Unauthorized'}, status=401)

        share_ids = []

        with transaction.atomic():
            for link_id in link_ids:
                try:
                    existing_link = Link.objects.get(id=link_id, user_id=session_user_id)
                except Link.DoesNotExist:
                    continue

                for user_id in user_ids:
                    try:
                        existing_user = User.objects.get(id=user_id)
                    except Link.DoesNotExist:
                        continue

                    attempts = 0
                    max_attempts = 5
                    while attempts < max_attempts:
                        share_id = uuid.uuid4().hex

                        try:
                            Share.objects.create(
                                id=share_id,
                                link=existing_link,
                                user=existing_user,
                                user_email=existing_user.email,
                                is_writable=1 if is_writable else 0,
                            )

                            share_ids.append(share_id)

                            break
                        except IntegrityError as error:
                            error_str = str(error).lower()

                            if 'unique' in error_str and 'link_id' in error_str and 'user_id' in error_str:
                                break
                            elif 'unique' in error_str and 'id' in error_str:
                                attempts += 1

                                continue
                            else:
                                raise error

        new_shares = Share.objects.filter(id__in=share_ids)

        if 0 < len(new_shares):
            return Response({
                'message': 'Shares created successfully.',
                'data': [
                    {
                        'id': new_share.id,
                        'link_id': new_share.link.id,
                        'user_id': new_share.user.id,
                        'user_email': new_share.user_email,
                        'is_writable': 1 if new_share.is_writable else 0,
                    }
                    for new_share in new_shares
                ]
            }, status=201)
        else:
            return Response({'message': 'No share created.'}, status=400)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)


@verify_token
@api_view(['GET'])
def get_shares(request, link_id):
    try:
        if not link_id:
            return Response({'message': 'Invalid Input'}, status=400)

        session_user_id = getattr(request, 'user_id', None)
        session_user_email = getattr(request, 'user_email', None)

        if not session_user_id or not session_user_email:
            return Response({'message': 'Unauthorized'}, status=401)

        existing_shares = Share.objects.filter(link_id=link_id, link__user_id=session_user_id)

        return Response({'message': '', 'data': [
            {
                'id': existing_share.id,
                'link_id': existing_share.link.id,
                'user_id': existing_share.user.id,
                'user_email': existing_share.user_email,
                'is_writable': 1 if existing_share.is_writable else 0,
            }
            for existing_share in existing_shares
        ]}, status=200)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)


@verify_token
@api_view(['DELETE', 'PUT'])
def remove_update_share(request, share_id):
    try:
        if request.method == 'DELETE':
            if not share_id:
                return Response({'message': 'Invalid Input'}, status=400)

            session_user_id = getattr(request, 'user_id', None)
            session_user_email = getattr(request, 'user_email', None)

            if not session_user_id or not session_user_email:
                return Response({'message': 'Unauthorized'}, status=401)

            deleted_share = Share.objects.filter(id=share_id, link__user_id=session_user_id).first()

            if not deleted_share:
                return Response({'message': 'No share removed.'}, status=400)

            deleted_count, _ = deleted_share.delete()

            if 0 < deleted_count:
                return Response({'message': 'Share removed successfully.'}, status=200)
            else:
                return Response({'message': 'No share removed.'}, status=400)
        elif request.method == 'PUT':
            is_writable = request.data.get('isWritable')

            if not share_id:
                return Response({'message': 'Invalid Input'}, status=400)

            session_user_id = getattr(request, 'user_id', None)
            session_user_email = getattr(request, 'user_email', None)

            if not session_user_id or not session_user_email:
                return Response({'message': 'Unauthorized'}, status=401)

            updated_share = Share.objects.filter(id=share_id, link__user_id=session_user_id).first()

            if not updated_share:
                return Response({'message': 'No share updated.'}, status=400)

            updated_share.is_writable = is_writable
            updated_share.save()

            return Response({'message': 'Share updated successfully.', 'data': {
                'id': updated_share.id,
                'link_id': updated_share.link.id,
                'user_id': updated_share.user.id,
                'user_email': updated_share.user_email,
                'is_writable': 1 if updated_share.is_writable else 0,
            }}, status=200)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)
