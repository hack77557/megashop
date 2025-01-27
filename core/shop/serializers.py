from rest_framework import serializers
from .models import Category, Product, ProductAttribute

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        ref_name = "ShopCategorySerializer"  # Унікальне ім'я для цього серіалізатора

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        ref_name = "ShopProductSerializer"  # Унікальне ім'я для цього серіалізатора

class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['attribute', 'value']  # Поля атрибутів (attribute.name і value)

    attribute = serializers.CharField(source='attribute.name')  # Виводимо назву атрибуту замість ID

class ProductDetailtSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(source='product_attributes', many=True)  # Пов'язане поле

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'brand', 'description', 'slug', 'price', 'image', 'available',
            'created_at', 'updated_at', 'discount', 'category', 'attributes'
        ]
        ref_name = "ShopProductDetailSerializer"  # Унікальне ім'я
