from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import (CategorySerializer, ProductSerializer,
                          RegisterSerializer, LoginSerializer, UserSerializer)
from .models import Category, Product


class CategoryView(ListAPIView):
    """Класс для просмотра категорий с подкатегориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductView(ListAPIView):
    """Класс для просмотра продуктов."""

    queryset = Product.objects.all() \
        .select_related('category', 'subcategory')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class RegisterView(APIView):
    """Класс для регистрации пользователя."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """Класс для авторизации пользователя."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(**serializer.validated_data)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
