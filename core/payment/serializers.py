# payment/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem
from shop.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_title', 'price', 'quantity', 'title', 'discount', 
                  'total_price', 'price_snapshot', 'discount_snapshot')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'shipping_address', 'total_price', 'is_paid', 'status', 
                  'payment_method', 'delivery_method', 'created_at', 'items')
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address', 'total_price', 'payment_method', 'delivery_method']