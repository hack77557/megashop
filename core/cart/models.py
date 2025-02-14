from django.db import models
from django.conf import settings
from shop.models import ProductProxy as Product  # Імпортуємо модель продукту з додатку shop

class Cart(models.Model):
    """
    Модель кошика, прив'язана до конкретного користувача.
    Використовується OneToOneField, тому кожен користувач має лише один кошик.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Кошик користувача {self.user.username}"

class CartItem(models.Model):
    """
    Модель для зберігання окремих елементів кошика.
    Кожен елемент пов'язаний з продуктом і кошиком.
    """
    cart = models.ForeignKey(Cart, related_name="cart_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')
        verbose_name = "Елемент кошика"
        verbose_name_plural = "Елементи кошика"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
