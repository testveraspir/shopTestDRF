from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import (CategorySerializer, ProductSerializer,
                          RegisterSerializer, LoginSerializer,
                          UserSerializer, CartSerializer, CartItemSerializer)
from .models import Category, Product, Cart, CartItem
from django.db import transaction


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


class CartDetailView(RetrieveAPIView):
    """Класс для просмотра корзины"""

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartAddUpdateView(APIView):
    """Класс для добавления/обновления товара"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        product = serializer.validated_data['product_slug']
        quantity = serializer.validated_data['quantity']
        cart, _ = Cart.objects.get_or_create(user=request.user)
        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(cart=cart,
                                                                product=product,
                                                                defaults={'quantity': quantity})
            if not created:
                cart_item.quantity = quantity
                cart_item.save()

        cart_serializer = CartSerializer(cart)
        if created:
            return Response({
                'message': 'Товар добавлен в корзину',
                'cart': cart_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Количество товара обновлено',
                'cart': cart_serializer.data
            }, status=status.HTTP_200_OK)


class CartRemoveView(DestroyAPIView):
    """Класс для удаления товара из корзины по product_slug"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart.cart_items.all()

    def get_object(self):
        product_slug = self.kwargs['product_slug']
        cart = Cart.objects.get(user=self.request.user)

        cart_item = get_object_or_404(CartItem,
                                      cart=cart,
                                      product__slug=product_slug)
        return cart_item

    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_object()
        cart = cart_item.cart
        cart_item.delete()

        return Response({
                'message': 'Товар успешно удален из корзины',
                'cart': CartSerializer(cart).data
            }, status=status.HTTP_200_OK)


class CartClearView(APIView):
    """Класс для полной очистки корзины"""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.cart_items.exists():
            return Response({'detail': 'Корзина уже пуста'},
                            status=status.HTTP_400_BAD_REQUEST)
        cart.cart_items.all().delete()
        return Response({'detail': 'Корзина успешно очищена'},
                        status=status.HTTP_200_OK)
