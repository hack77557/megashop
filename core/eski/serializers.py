from rest_framework import serializers
from shop.models import Category, Product
from payment.models import Order, OrderItem






class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'shipping_address', 'total_price', 'is_paid',
            'payment_method', 'delivery_method', 'created_at', 'items'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address', 'total_price', 'payment_method', 'delivery_method']
'''
#користувач
from django.contrib.auth.models import User
#from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions']
        #fields = '__all__'
        ref_name = "EskiUserSerializer"
'''
from django.contrib.auth import get_user_model
#from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Явно перелічуємо поля, які ми хочемо включити
        fields = (
            'id',
            'last_login',
            'is_superuser',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
            'groups',
            'user_permissions',
            'middle_name',
            'phone',
            'date_of_birth',
            'sex',
            'language',
            # Якщо вам не потрібні groups та user_permissions — не включайте їх
        )
        ref_name = 'CustomUser'
        