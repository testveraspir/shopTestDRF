from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
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


@extend_schema(
    tags=['catalog'],
    summary="Список категорий",
    description="Возвращает список всех категорий с подкатегориями",
    responses={200: CategorySerializer(many=True)},
    auth=[]
)
class CategoryView(ListAPIView):
    """Просмотр категорий с подкатегориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=['catalog'],
    summary="Список товаров",
    description="Возвращает список всех товаров с детальной информацией",
    responses={200: ProductSerializer(many=True)},
    auth=[]
)
class ProductView(ListAPIView):
    """Просмотр списка продуктов."""

    queryset = Product.objects.all() \
        .select_related('category', 'subcategory')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=['auth'],
    summary="Регистрация пользователя",
    description="Создает нового пользователя и возвращает токен авторизации",
    auth=[],
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(
            description="Пользователь успешно создан",
            response={
                "type": "object",
                "properties": {
                    "user": {"type": "object"},
                    "token": {"type": "string",
                              "example": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
                }
            }
        ),
        400: OpenApiResponse(description="Ошибка валидации")
    }
)
class RegisterView(APIView):
    """Регистрация нового пользователя."""

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


@extend_schema(
    tags=['auth'],
    summary="Авторизация пользователя",
    description="Вход в систему по username/password. Возвращает токен авторизации",
    auth=[],
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Успешный вход",
            response={
                "type": "object",
                "properties": {
                    "user": {"type": "object"},
                    "token": {"type": "string",
                              "example": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
                }
            }
        ),
        400: OpenApiResponse(description="Неверные учетные данные"),
        401: OpenApiResponse(description="Не удалось аутентифицировать")
    }
)
class LoginView(APIView):
    """Авторизация пользователя."""

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


@extend_schema(
    tags=['cart'],
    summary="Просмотр корзины",
    description="Возвращает текущую корзину пользователя со всеми товарами",
    responses={200: CartSerializer}
)
class CartDetailView(RetrieveAPIView):
    """Просмотр корзины текущего пользователя."""

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


@extend_schema(
    tags=['cart'],
    summary="Добавление или обновление товара в корзине",
    description="""
    Добавляет новый товар в корзину или обновляет количество существующего.

    - Если товара нет в корзине - создаётся новая позиция
    - Если товар уже есть - обновляется его количество
    """,
    request=CartItemSerializer,
    responses={
        200: CartSerializer,
        201: CartSerializer,
        400: OpenApiResponse(description="Ошибка валидации"),
        401: OpenApiResponse(description="Не авторизован")
    }
)
class CartAddUpdateView(APIView):
    """Добавление или обновление товара в корзине."""

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


@extend_schema(
    tags=['cart'],
    summary="Удаление товара из корзины",
    description="Удаляет конкретный товар по slug из корзины пользователя.",
    parameters=[
        OpenApiParameter(
            name='product_slug',
            description='Slug товара, который нужно удалить',
            required=True,
            type=str,
            location=OpenApiParameter.PATH)
    ],
    responses={
        200: OpenApiResponse(
            description="Товар успешно удален",
            response=CartSerializer
        ),
        401: OpenApiResponse(description="Не авторизован"),
        404: OpenApiResponse(description="Товар не найден в корзине")
    }
)
class CartRemoveView(DestroyAPIView):
    """Удаление товара из корзины по product_slug."""

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


@extend_schema(
    tags=['cart'],
    summary="Очистка корзины",
    description="Полностью удаляет все товары из корзины текущего пользователя",
    request=None,
    responses={
        200: OpenApiResponse(description="Корзина успешно очищена"),
        400: OpenApiResponse(description="Корзина уже пуста"),
        401: OpenApiResponse(description="Не авторизован")
    }
)
class CartClearView(APIView):
    """Полная очистка корзины пользователя."""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.cart_items.exists():
            return Response({'detail': 'Корзина уже пуста'},
                            status=status.HTTP_400_BAD_REQUEST)
        cart.cart_items.all().delete()
        return Response({'detail': 'Корзина успешно очищена'},
                        status=status.HTTP_200_OK)
