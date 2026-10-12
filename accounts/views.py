from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet

from accounts.serializers import LoginSerializer


class AuthenticationViewSet(ViewSet):
    permission_classes = [AllowAny]

    @action(methods=['post'], detail=False, url_path="")
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data['email']
        user = User.objects.create_user(username=username, email=email, password=password)
        serializer = LoginSerializer(user)
        return Response(serializer.data)
