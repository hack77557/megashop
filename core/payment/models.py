from django.db import models
#from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from decimal import Decimal

from shop.models import Product
#User = get_user_model()
from django.conf import settings  # Імпортуємо settings


class ShippingAddress(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)

    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)

    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=100, blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Addresses'
        ordering = ['-id']
    
    def __str__(self):
        return f"ShippingAddress obj id: {self.id}, \
            related: (User name - {self.user.username})"

    def get_absolute_url(self):
        return f"/payments/shipping-address"
    
    @classmethod
    def create_default_shipping_address(cls, user):
        default_shipping_address = {
            "user": user, "full_name": "Noname", "email": "email@example.com",
            "street_address": "fill address", "apartment_address": "fill address", "country": ""
        }
        shipping_address = cls(**default_shipping_address)
        shipping_address.save()
        return shipping_address



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE, blank=True, null=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    # Додаємо нові поля
    #payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    #delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='nova_poshta')

        # 🔹 Збільшуємо `max_length` для запобігання помилкам
    payment_method = models.CharField(max_length=20, choices=[
        ('stripe-payment', 'Stripe'),
        ('yookassa-payment', 'Yookassa'),
        ('cash-on-delivery', 'Cash on Delivery')
    ], default='cash-on-delivery')

    delivery_method = models.CharField(max_length=20, choices=[
        ('nova_poshta', 'Nova Poshta'),
        ('ukrposhta', 'Ukrposhta'),
        ('courier', 'Courier'),
        ('self_pickup', 'Self Pickup')
    ], default='nova_poshta')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_price__gte=0),
                name='total_price_gte_0',
            )
        ]
    def __str__(self):
        return f"Order id: {self.id}, related: (User - {self.user.username if self.user else 'Guest'}) (Status - {self.is_paid})"    



    def get_absolute_url(self):
        return reverse("payment:order-detail", kwargs={'pk': self.pk})
    
    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())

    @property
    def get_discount(self):
        if (total_cost := self.get_total_cost_before_discount()) and self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField(default=1)
    title = models.CharField(max_length=255, blank=True)  # Назва товару
    discount = models.IntegerField(default=0)  # Знижка на момент замовлення
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'
        ordering = ['-id']
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=0),
                name='quantity_gte_0',
            ),
        ]

    def __str__(self):
        order_id = self.order.id if self.order else "No Order"
        product_title = self.product.title if self.product else "Unknown Product"
        return f"OrderItem id: {self.id}, related: (Order id - {order_id}, Product title - {product_title})"

    def save(self, *args, **kwargs):
        if not self.title and self.product:  # Фіксуємо назву при створенні
            self.title = self.product.title
        if not self.discount and self.product:  # Фіксуємо знижку
            self.discount = self.product.discount
        super().save(*args, **kwargs)

    def get_cost(self):
        return self.price * self.quantity
    
    @property
    def total_cost(self):
        return self.price * self.quantity
    
    @classmethod
    def get_totat_quantity_for_product(cls, product):
        return cls.objects.filter(product=product).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
    
    @staticmethod
    def get_average_price():
        return OrderItem.objects.aggregate(average_price=models.Avg('price'))['average_price']
    