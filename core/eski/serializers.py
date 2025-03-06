from rest_framework import serializers
from shop.models import Category, Product
from django.contrib.auth import get_user_model

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CustomDateField(serializers.DateField):
    def to_internal_value(self, data):
        if data == '':
            return None
        return super().to_internal_value(data)
    
class UserSerializer(serializers.ModelSerializer):

    # Перевизначення поля, щоб зробити його необов’язковим
    date_of_birth = CustomDateField(required=False, allow_null=True)

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

'''

from payment.models import Order, OrderItem



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








class UserSerializer(serializers.ModelSerializer):

    # Перевизначення поля, щоб зробити його необов’язковим
    date_of_birth = CustomDateField(required=False, allow_null=True)

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


'''