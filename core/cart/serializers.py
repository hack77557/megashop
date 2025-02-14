from rest_framework import serializers
from shop.models import ProductProxy as Product  # Ми імпортуємо ProductProxy як Product
from .models import Cart, CartItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # Замінюємо 'name' на 'title', якщо саме так називається поле у ProductProxy
        fields = ['id', 'title', 'price']

class CartItemSerializer(serializers.ModelSerializer):
    # Повертаємо інформацію про продукт через вкладений серіалізатор.
    product = ProductSerializer(read_only=True)
    # Для запису приймаємо лише product_id
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    # Виводимо всі елементи кошика.
    cart_items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items']
        read_only_fields = ['user']
