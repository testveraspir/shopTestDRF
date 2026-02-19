from django.urls import path
from .views import (CategoryView, ProductView, RegisterView,
                    LoginView, CartDetailView, CartAddUpdateView)

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('products/', ProductView.as_view(), name='product-list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/items/', CartAddUpdateView.as_view(), name='cart-add-update'),

]
