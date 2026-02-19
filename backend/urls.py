from django.urls import path
from .views import (CategoryView, ProductView, RegisterView,
                    LoginView, CartDetailView, CartAddUpdateView,
                    CartRemoveView, CartClearView)

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('products/', ProductView.as_view(), name='product-list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/items/', CartAddUpdateView.as_view(), name='cart-add-update'),
    path('cart/items/<slug:product_slug>/', CartRemoveView.as_view(), name='cart-remove'),
    path('cart/clear/', CartClearView.as_view(), name='cart-clear'),

]
