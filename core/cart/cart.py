from decimal import Decimal, ROUND_HALF_UP
from shop.models import ProductProxy
from django.http import HttpRequest

'''
class Cart():
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get('session_key')

        if not cart:
            cart = self.session['session_key'] = {}

        self.cart = cart
        self.clean_cart()  # ✅ Автоматично чистимо кошик

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())

    def __iter__(self):
        product_ids = list(self.cart.keys())
        products = {str(p.id): p for p in ProductProxy.objects.filter(id__in=product_ids)}
        cart = self.cart.copy()

        for product_id in list(cart.keys()):
            if product_id not in products:
                # ✅ Видаляємо товар, якого немає в БД
                del self.cart[product_id]
                continue

            product = products[product_id]
            cart[product_id]['product_id'] = product.id  # ✅ Зберігаємо лише ID
            cart[product_id]['title'] = product.title  # ✅ Додаємо назву
            cart[product_id]['price'] = float(product.get_discounted_price())  # ✅ Оновлюємо ціну

        self.session.modified = True

        for item in cart.values():
            item['total'] = item['price'] * item['qty']
            yield item

    def add(self, product: ProductProxy, quantity):
        product_id = str(product.id)
        discounted_price = float(product.get_discounted_price())  # ✅ Перетворюємо `Decimal` в `float`

        if product_id not in self.cart:
            self.cart[product_id] = {'qty': quantity, 'price': discounted_price, 'title': product.title}

        self.cart[product_id]['qty'] = quantity
        self.session.modified = True
'''
class Cart():
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get('session_key')

        if not cart:
            cart = self.session['session_key'] = {}

        self.cart = cart

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())


    def __iter__(self):
        """Отримуємо список товарів за їх ID і додаємо до об'єктів у кошику"""
        product_ids = self.cart.keys()
        products = ProductProxy.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = {
                'id': product.id,
                'title': product.title,
                'price': str(product.get_discounted_price()),  # Ціна може змінюватися
                'image': product.image.url if product.image else None,
            }

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total'] = item['price'] * item['qty']
            yield item

    def add(self, product: ProductProxy, quantity):
        """Додаємо товар до кошика, зберігаючи тільки необхідні дані"""
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'qty': quantity,
                'price': str(product.get_discounted_price()),  # Зберігаємо як str для JSON
            }
        else:
            self.cart[product_id]['qty'] = quantity

        self.session.modified = True



    def delete(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

    def clear(self):
        self.cart = {}
        self.session['session_key'] = self.cart
        self.session.modified = True

    def update(self, product_id, new_quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id]['qty'] = new_quantity
            self.session.modified = True

    def get_total_price(self):
        total = sum(Decimal(item['price']) * item['qty'] for item in self.cart.values())

        # ✅ Завжди перетворюємо total в Decimal, навіть якщо він 0
        return Decimal(total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def clean_cart(self):
        """✅ Видаляє товари, яких більше немає в БД"""
        product_ids = list(self.cart.keys())
        existing_products = {str(p.id) for p in ProductProxy.objects.filter(id__in=product_ids)}

        for product_id in product_ids:
            if product_id not in existing_products:
                del self.cart[product_id]
                print(f"⚠️ Видалено товар з ID {product_id}, бо його немає в БД")

        self.session.modified = True
