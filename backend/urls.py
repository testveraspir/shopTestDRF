from django.urls import path
from .views import CategoryView, ProductView

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('products/', ProductView.as_view(), name='product-list'),
]
