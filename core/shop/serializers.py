from rest_framework import serializers
from .models import Category#, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        ref_name = "Shop_Product"  # Унікальне ім'я для цього серіалізатора
'''
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        ref_name = "Shop_Product"  # Унікальне ім'я для цього серіалізатора
'''

