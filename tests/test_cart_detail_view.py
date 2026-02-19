from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from backend.models import (Product, Cart, CartItem,
                            Category, Subcategory)

User = get_user_model()


class CartDetailViewTests(APITestCase):
    """Тесты для получения корзины"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('cart-detail')

        self.category = Category.objects.create(name='Электроника')
        self.subcategory = Subcategory.objects.create(category=self.category,
                                                      name='Телефон')
        self.product1 = Product.objects.create(name='Смартфон1',
                                               price=Decimal('100.00'),
                                               category=self.category,
                                               subcategory=self.subcategory)

        self.product2 = Product.objects.create(name='Смартфон2',
                                               price=Decimal('500.00'),
                                               category=self.category,
                                               subcategory=self.subcategory)

    def test_get_cart_authenticated(self):
        """Тест получения корзины авторизованным пользователем"""

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart,
                                product=self.product1,
                                quantity=2)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertIn('total_items', response.data)
        self.assertIn('total_price', response.data)

    def test_get_cart_unauthenticated(self):
        """Тест получения корзины неавторизованным пользователем"""

        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_get_cart_with_multiple_items(self):
        """Тест получения корзины с несколькими товарами"""

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart,
                                product=self.product1,
                                quantity=2)
        CartItem.objects.create(cart=cart,
                                product=self.product2,
                                quantity=1)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['total_items'], 3)
        self.assertEqual(Decimal(response.data['total_price']),
                         Decimal('700.00'))
