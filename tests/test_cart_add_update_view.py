from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from backend.models import (Product, Cart, CartItem,
                            Category, Subcategory)

User = get_user_model()


class CartAddUpdateViewTests(APITestCase):
    """Тесты для добавления/обновления товаров в корзине"""

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

        self.url = reverse('cart-add-update')

    def test_add_new_item_to_cart(self):
        """Тест успешного добавления товара в корзину"""

        data = {
            'product_slug': self.product1.slug,
            'quantity': 2
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Товар добавлен в корзину')

        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, product=self.product1)
        self.assertEqual(cart_item.quantity, 2)
        self.assertIn('cart', response.data)
        self.assertIn('items', response.data['cart'])

    def test_add_item_invalid_quantity_zero(self):
        """Тест добавления товара с количеством 0"""

        data = {
            'product_slug': self.product1.slug,
            'quantity': 0
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Validation failed')
        self.assertIn('quantity', response.data['details'])

    def test_add_item_invalid_quantity_negative(self):
        """Тест добавления товара с отрицательным количеством"""

        data = {
            'product_slug': self.product1.slug,
            'quantity': -5
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Validation failed')

    def test_add_nonexistent_product(self):
        """Тест добавления несуществующего товара"""

        data = {
            'product_slug': 'technika',
            'quantity': 1
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_slug', response.data['details'])

    def test_add_item_missing_quantity(self):
        """Тест добавления товара с отсутствующим quantity"""

        data = {
            'product_slug': self.product1.slug
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data['details'])

    def test_add_item_missing_product_slug(self):
        """Тест добавления товара с отсутствующим product_slug"""

        data = {
            'quantity': 2
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_slug', response.data['details'])

    def test_update_existing_item_quantity(self):
        """Тест обновления количества существующего товара"""

        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart,
                                            product=self.product1,
                                            quantity=1)
        data = {
            'product_slug': self.product1.slug,
            'quantity': 5
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Количество товара обновлено')
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_add_item_unauthenticated(self):
        """Тест добавления товара без авторизации"""

        self.client.force_authenticate(user=None)
        data = {
            'product_slug': self.product1.slug,
            'quantity': 2
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_multiple_different_items(self):
        """Тест добавления нескольких разных товаров"""

        data1 = {
            'product_slug': self.product1.slug,
            'quantity': 2
        }
        response1 = self.client.post(self.url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        data2 = {
            'product_slug': self.product2.slug,
            'quantity': 1
        }
        response2 = self.client.post(self.url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.cart_items.count(), 2)
        response = self.client.get(reverse('cart-detail'))
        self.assertEqual(Decimal(response.data['total_price']),
                         Decimal('700.00'))
