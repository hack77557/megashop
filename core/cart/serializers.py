'''
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
'''

from rest_framework import serializers
from shop.models import ProductProxy as Product  # Ми імпортуємо ProductProxy як Product
from .models import Cart, CartItem


class ProductSerializer(serializers.ModelSerializer):
    """
    Серіалізатор продукту для кошика.
    """
    current_price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    discount = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'current_price', 'image', 'discount']

    def get_current_price(self, obj):
        """Повертає поточну ціну з урахуванням знижки."""
        return obj.get_discounted_price()

    def get_image(self, obj):
        """Повертає URL головного зображення товару."""
        return obj.image.url if obj.image else None


class CartItemSerializer(serializers.ModelSerializer):
    """
    Серіалізатор елементу кошика.
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    total_price_before_discount = serializers.SerializerMethodField()
    total_price_with_discount = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price_before_discount', 'total_price_with_discount']

    def get_total_price_before_discount(self, obj):
        """Розраховує загальну вартість товару без урахування знижки."""
        return round(obj.product.price * obj.quantity, 2)

    def get_total_price_with_discount(self, obj):
        """Розраховує загальну вартість товару з урахуванням знижки."""
        return round(obj.product.get_discounted_price() * obj.quantity, 2)


class CartSerializer(serializers.ModelSerializer):
    """
    Серіалізатор кошика, який підраховує загальну суму.
    """
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price_before_discount = serializers.SerializerMethodField()
    total_price_with_discount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items', 'total_price_before_discount', 'total_price_with_discount']
        read_only_fields = ['user']

    def get_total_price_before_discount(self, obj):
        """Підраховує загальну вартість кошика без знижки."""
        return sum(item.product.price * item.quantity for item in obj.cart_items.all())

    def get_total_price_with_discount(self, obj):
        """Підраховує загальну вартість кошика з урахуванням знижок."""
        return sum(item.product.get_discounted_price() * item.quantity for item in obj.cart_items.all())
