from rest_framework import serializers
from .models import Category, Subcategory, Product
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


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
