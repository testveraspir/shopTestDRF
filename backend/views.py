from rest_framework.generics import ListAPIView
from .serializers import CategorySerializer, ProductSerializer
from .models import Category, Product


class CategoryView(ListAPIView):
    """Класс для просмотра категорий с подкатегориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductView(ListAPIView):
    """Класс для просмотра продуктов."""

    queryset = Product.objects.all() \
        .select_related('category', 'subcategory')
    serializer_class = ProductSerializer
