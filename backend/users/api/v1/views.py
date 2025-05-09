from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.api.v1.serializers import UserSerializer
from users.models import User


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UserSerializer,
        responses={201: UserSerializer, 400: "Bad Request"},
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DoctorList(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Get a list of all doctors",
        responses={200: UserSerializer(many=True)},
        tags=["Users"],
    )
    def get(self, request):
        doctors = User.objects.filter(is_doctor=True)
        serializer = UserSerializer(doctors, many=True)
        return Response(serializer.data)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Get the current user's profile",
        responses={200: UserSerializer},
        tags=["Users"],
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
