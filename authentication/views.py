from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User
from authentication.serializers import UserSerializer, ChangePasswordSerializer


class AuthenticationViewSet(ViewSet):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            }
        ),
        responses={
            200: openapi.Response('Login successful', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
        },
        operation_summary="User Login",
        operation_description="User login",
        tags=['Auth'],
    )
    def login(self, request, *args, **kwargs):
        data = request.data
        user = User.objects.filter(username=data.get('username')).first()
        if not user:
            return Response(data={'result': '', 'error': 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if not check_password(data.get('password'), user.password):
            return Response(data={'result': '', 'error': 'Incorrect Password'}, status=status.HTTP_400_BAD_REQUEST)
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        access_token['role'] = user.role
        return Response(data={'result': {'access_token': str(access_token), 'refresh_token': str(refresh_token)}},
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={200: UserSerializer()},
        operation_summary="Create New User",
        operation_description="Create a new user",
        tags=['Auth'],
    )
    def register(self, request, *args, **kwargs):
        data = request.data
        serializer = UserSerializer(data=data)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={200: UserSerializer()},
        operation_summary="Get User Details",
        operation_description="Get user details",
        tags=['Auth'],
    )
    def auth_me(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.user.id).first()
        return Response(data={'result': UserSerializer(user).data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={200: UserSerializer()},
        operation_summary='Change User Password',
        operation_description='Change user password',
        tags=['Auth']
    )
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not check_password(old_password, user.password):
            return Response(data={'result': '', 'error': 'Password is incorrect!'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.save()
        return Response(data={'result': UserSerializer(user).data}, status=status.HTTP_200_OK)
