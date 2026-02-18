from rest_framework import serializers
from .models import Category, Subcategory, Product


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
