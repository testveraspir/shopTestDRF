from rest_framework import serializers
from .models import Category, Subcategory, Product, Cart, CartItem
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'slug', 'image']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'subcategories']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name',
                                          read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name',
                                             read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price',
                  'category_name', 'subcategory_name', 'images']

    def get_images(self, obj):
        if not obj.image:
            return []
        return [
            obj.image_small.url,
            obj.image_medium.url,
            obj.image_large.url
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return data
        raise serializers.ValidationError('Неверные данные')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class CartItemSerializer(serializers.ModelSerializer):
    product_slug = serializers.SlugRelatedField(slug_field='slug',
                                                queryset=Product.objects.all(),
                                                write_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price',
                                             max_digits=10,
                                             decimal_places=2,
                                             read_only=True)
    total_price = serializers.SerializerMethodField()
    quantity = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = CartItem
        fields = ['id', 'product_slug', 'product_name',
                  'product_price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cart_items',
                               many=True,
                               read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price']

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.cart_items.all())

    def get_total_price(self, obj):
        return sum(item.total_price for item in obj.cart_items.all())
