from rest_framework import serializers
from .models import Category, Product, ProductAttribute, Attribute

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  # Додаємо підтримку зображень

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at', 'parent', 'image']  # Додаємо `image`
        ref_name = "ShopCategorySerializer"


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['attribute', 'value']  # Поля атрибутів (attribute.name і value)

    attribute = serializers.CharField(source='attribute.name')  # Виводимо назву атрибуту замість ID
    

'''v1
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        #fields = '__all__'
        fields = [
            'id', 'title', 'brand', 'slug', 'price', 'image', 'available', 'category'
        ]
        ref_name = "ShopProductSerializer"  # Унікальне ім'я для цього серіалізатора
'''
class ProductSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            #'id', 'title', 'brand', 'slug', 'price', 'image', 'available', 'category', 'attributes'
            'id', 'title', 'brand', 'description', 'slug', 'price', 'purchase_price', 'image', 'available', 'discount', 'category', 'attributes'
        ]
        ref_name = "ShopProductSerializer"

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        product = Product.objects.create(**validated_data)

        for attr in attributes_data:
            attribute_name = attr.get('attribute')
            value = attr.get('value')

            # 🔥 Якщо атрибут існує → використовуємо його, якщо ні → створюємо
            attribute, created = Attribute.objects.get_or_create(name=attribute_name)

            # 🔥 Перевіряємо, чи існує така характеристика для цього продукту
            ProductAttribute.objects.update_or_create(
                product=product, attribute=attribute, defaults={"value": value}
            )

        return product


class ProductDetailtSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(source='product_attributes', many=True)  # Пов'язане поле

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'brand', 'description', 'slug', 'price', 'purchase_price', 'image', 'available',
            'created_at', 'updated_at', 'discount', 'category', 'attributes'
        ]
        ref_name = "ShopProductDetailSerializer"  # Унікальне ім'я

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']  # Використовуємо коректні поля