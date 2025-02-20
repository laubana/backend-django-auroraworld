import datetime
import uuid

import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import User


@api_view(['GET'])
def refresh(request):
    try:
        refresh_token = request.COOKIES.get('refreshToken')

        if not refresh_token:
            return Response({'message': 'Refresh failed.'}, status=401)

        access_token_secret = settings.ACCESS_TOKEN_SECRET
        refresh_token_secret = settings.REFRESH_TOKEN_SECRET

        if not access_token_secret or not refresh_token_secret:
            return Response({'message': 'Refresh failed.'}, status=401)

        result = jwt.decode(refresh_token, refresh_token_secret, algorithms=['HS256'])

        user_id = result.get('id')

        if not user_id:
            return Response({'message': 'Refresh failed.'}, status=401)

        try:
            existing_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'Refresh failed.'}, status=401)

        access_token = jwt.encode({
            'id': existing_user.id,
            'email': existing_user.email,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        }, access_token_secret, algorithm='HS256')

        return Response({
            'message': 'Refreshed successfully.',
            'data': {
                'accessToken': access_token,
                'id': existing_user.id,
                'email': existing_user.email,
            },
        }, status=200)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)


@api_view(['POST'])
def sign_in(request):
    try:
        email = request.data.get('email').strip()
        password = request.data.get('password').strip()

        if not email or not password:
            return Response({'message': 'Invalid Input'}, status=400)

        try:
            existing_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Sign-in failed.'}, status=401)

        is_match = check_password(password, existing_user.password)

        if not is_match:
            return Response({'message': 'Sign-in failed.'}, status=401)

        access_token_secret = settings.ACCESS_TOKEN_SECRET
        refresh_token_secret = settings.REFRESH_TOKEN_SECRET

        if not access_token_secret or not refresh_token_secret:
            return Response({'message': 'Sign-in failed.'}, status=401)

        access_token = jwt.encode({
            'id': existing_user.id,
            'email': existing_user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, access_token_secret, algorithm='HS256')

        refresh_token = jwt.encode({
            'id': existing_user.id,
            'email': existing_user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, refresh_token_secret, algorithm='HS256')

        response = Response({
            'message': 'Signed in successfully.',
            'data': {
                'accessToken': access_token,
                'id': existing_user.id,
                'email': existing_user.email
            }
        }, status=200)

        response.set_cookie(
            key='refreshToken',
            value=refresh_token,
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            samesite='None',
            secure=True
        )

        return response
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)


@api_view(['POST'])
def sign_out(request):
    try:
        response = Response({'message': 'Signed out successfully.'}, status=200)

        response.delete_cookie('refreshToken')

        return response
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)


@api_view(['POST'])
def sign_up(request):
    try:
        email = request.data.get('email').strip()
        password = request.data.get('password').strip()

        if not email or not password:
            return Response({'message': 'Invalid Input'}, status=400)

        existing_users = User.objects.filter(email=email)

        if len(existing_users) != 0:
            return Response({'message': 'User already exists.'}, status=409)

        hashed_password = make_password(password)

        new_user = None

        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            user_id = uuid.uuid4().hex

            try:
                new_user = User.objects.create(
                    id=user_id,
                    email=email,
                    password=hashed_password
                )

                break
            except IntegrityError as error:
                error_str = str(error).lower()

                if 'users.email' in error_str:
                    return Response({'message': 'User already exists.'}, status=409)
                elif 'users.id' in error_str:
                    attempts += 1

                    continue
                else:
                    raise error

        return Response({
            'message': 'User created successfully.',
            'data': {
                'id': new_user.id,
                'email': new_user.email,
            },
        }, status=201)
    except Exception as error:
        print(error)

        return Response({'message': 'Server Error'}, status=500)
