from rest_framework.generics import ListAPIView
from .serializers import CategorySerializer
from .models import Category


class CategoryView(ListAPIView):
    """Класс для просмотра категорий с подкатегориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
