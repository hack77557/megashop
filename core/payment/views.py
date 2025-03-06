# payment/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpRequest, JsonResponse
from django.urls import reverse
from decimal import Decimal
import uuid
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.templatetags.static import static
import weasyprint

from .forms import ShippingAddressForm
from .models import Order, OrderItem, ShippingAddress
from cart.models import Cart as CartModel, CartItem
from shop.models import Product
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer, OrderItemSerializer  # Змінено шлях імпорту

# Payment APIs
import stripe
from yookassa import Payment, Configuration

#from cart.cart import Cart
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Stripe configuration
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION
# Yookassa configuration
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

@login_required(login_url='account:login')
def shipping_view(request: HttpRequest):
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        shipping_address = None

    form = ShippingAddressForm(instance=shipping_address)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('payment:checkout')
    context = {'form': form}
    return render(request, 'shipping/shipping.html', context)

def checkout_view(request: HttpRequest):
    if request.user.is_authenticated:
        try:
            shipping_address = ShippingAddress.objects.get(user=request.user)
            context = {'shipping_address': shipping_address}
            return render(request, 'payment/checkout.html', context)
        except ShippingAddress.DoesNotExist:
            return redirect('payment:shipping')
    return render(request, 'payment/checkout.html')

@login_required(login_url='account:login')
def complete_order(request: HttpRequest):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Отримуємо спосіб оплати та доставки
    payment_type = request.POST.get('payment-method', 'cash-on-delivery')
    delivery_method = request.POST.get('delivery-method', 'nova_poshta')

    print(f"🛒 Delivery method from POST request: {delivery_method}")
    print(f"💳 Payment method from POST request: {payment_type}")

    # Отримуємо дані користувача
    name = request.POST.get('name')
    email = request.POST.get('email')
    street_address = request.POST.get('street_address')
    apartment_address = request.POST.get('apartment_address')
    country = request.POST.get('country')
    city = request.POST.get('city')
    zip_code = request.POST.get('zip_code')

    # Отримуємо кошик із моделі
    try:
        cart = CartModel.objects.get(user=request.user)
    except CartModel.DoesNotExist:
        return JsonResponse({'error': 'Your cart does not exist'}, status=400)

    cart_items = cart.cart_items.all()
    if not cart_items:
        return JsonResponse({'error': 'Your cart is empty'}, status=400)

    # Обчислюємо загальну ціну
    total_price = sum(item.product.get_discounted_price() * item.quantity for item in cart_items)

    # Отримуємо або створюємо адресу доставки
    shipping_address, _ = ShippingAddress.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': name,
            'email': email,
            'street_address': street_address,
            'apartment_address': apartment_address,
            'country': country,
            'city': city,
            'zip_code': zip_code,
        }
    )

    # Створюємо замовлення
    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        total_price=total_price,
        is_paid=False,
        delivery_method=delivery_method,
        payment_method=payment_type,
    )

    # Переносимо товари з CartItem в OrderItem
    items = []
    for cart_item in cart_items:
        print(f"✅ Cart item: {cart_item.product.title}, qty: {cart_item.quantity}")
        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            price=cart_item.product.get_discounted_price(),
            quantity=cart_item.quantity,
            title=cart_item.product.title,
            discount=cart_item.product.discount,
            user=request.user
        )
        items.append({
            'product': cart_item.product.title,
            'price': float(cart_item.product.get_discounted_price()),
            'quantity': cart_item.quantity,
        })

    # 🛒 **Очищаємо кошик після покупки**
    #cart.clear()

    # Логіка обробки оплати
    if payment_type == "stripe-payment":
        session_data = {
            'mode': 'payment',
            'success_url': request.build_absolute_uri(reverse('payment:payment-success')),
            'cancel_url': request.build_absolute_uri(reverse('payment:payment-fail')),
            'line_items': [
                {
                    'price_data': {
                        'unit_amount': int(item['price'] * Decimal(100)),
                        'currency': 'usd',
                        'product_data': {'name': item['product']},
                    },
                    'quantity': item['quantity'],
                } for item in items
            ],
            'client_reference_id': str(order.id),
        }
        session = stripe.checkout.Session.create(**session_data)
        cart.cart_items.all().delete()  # Очищаємо кошик перед перенаправленням
        return redirect(session.url, code=303)

    elif payment_type == "yookassa-payment":
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create({
            "amount": {"value": str(total_price * 93), "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(reverse('payment:payment-success')),
            },
            "capture": True,
            "test": True,
            "description": "Замовлення в магазині",
            "metadata": {"order_id": str(order.id)},
        }, idempotence_key)
        cart.cart_items.all().delete()  # Очищаємо кошик перед перенаправленням
        return redirect(payment.confirmation.confirmation_url)

    elif payment_type == "cash-on-delivery":
        cart.cart_items.all().delete()  # Очищаємо кошик
        return JsonResponse({
            'message': 'Order created successfully',
            'order_id': order.id,
            'delivery_method': delivery_method,
            'payment_method': payment_type,
            'items': items
        })

    return JsonResponse({'error': 'Unsupported payment type'}, status=400)

def payment_success(request: HttpRequest):
    order_id = request.GET.get('order_id') or request.session.get('order_id')
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        order.is_paid = True
        order.save()
    # Очищаємо сесію (залишаємо для сумісності, якщо використовується)
    for key in list(request.session.keys()):
        if key == 'session_key' or key.startswith('cart'):
            del request.session[key]
    return render(request, 'payment/payment_success.html')

def payment_fail(request: HttpRequest):
    return render(request, 'payment/payment_fail.html')

@staff_member_required
def admin_order_pdf(request: HttpRequest, order_id):
    try:
        order = Order.objects.select_related('user', 'shipping_address').get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order doesn't exist or not found")
    html = render_to_string('payment/order/pdf/pdf_invoice.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f"filename=order_{order.id}.pdf"  # Виправив 'Content-Dispposition'
    css_path = static('payment/css/pdf.css').lstrip('/')
    stylesheets = [weasyprint.CSS(css_path)]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response


############################################################## API ########################################################################################################
@swagger_auto_schema(
    method='post',
    operation_description="Create a new order with items from the user's cart.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Full name of the customer'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            'street_address': openapi.Schema(type=openapi.TYPE_STRING, description='Street address'),
            'apartment_address': openapi.Schema(type=openapi.TYPE_STRING, description='Apartment number'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description='Country'),
            'city': openapi.Schema(type=openapi.TYPE_STRING, description='City'),
            'zip_code': openapi.Schema(type=openapi.TYPE_STRING, description='Postal code'),
            'payment_method': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['stripe-payment', 'yookassa-payment', 'cash-on-delivery'],
                description='Payment method'
            ),
            'delivery_method': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['nova_poshta', 'ukrposhta', 'courier', 'self_pickup'],
                description='Delivery method'
            ),
        },
        required=['name', 'email', 'street_address', 'country', 'city', 'zip_code'],
        example={
            'name': 'Іван Іванов',
            'email': 'ivan@example.com',
            'street_address': 'вул. Головна 1',
            'apartment_address': 'кв. 10',
            'country': 'Україна',
            'city': 'Київ',
            'zip_code': '01001',
            'payment_method': 'cash-on-delivery',
            'delivery_method': 'nova_poshta'
        }
    ),
    responses={
        201: openapi.Response('Order created', OrderSerializer),
        400: 'Invalid request or empty cart'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_complete_order(request):
    if request.method != 'POST':
        return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = request.data
    payment_type = data.get('payment_method', 'cash-on-delivery')
    delivery_method = data.get('delivery_method', 'nova_poshta')
    name = data.get('name')
    email = data.get('email')
    street_address = data.get('street_address')
    apartment_address = data.get('apartment_address')
    country = data.get('country')
    city = data.get('city')
    zip_code = data.get('zip_code')

    print(f"🛒 API Delivery method: {delivery_method}")
    print(f"💳 API Payment method: {payment_type}")

    try:
        cart = CartModel.objects.get(user=request.user)
    except CartModel.DoesNotExist:
        return Response({'error': 'Your cart does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    cart_items = cart.cart_items.all()
    if not cart_items:
        return Response({'error': 'Your cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

    total_price = sum(item.product.get_discounted_price() * item.quantity for item in cart_items)

    shipping_address, _ = ShippingAddress.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': name,
            'email': email,
            'street_address': street_address,
            'apartment_address': apartment_address,
            'country': country,
            'city': city,
            'zip_code': zip_code,
        }
    )

    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        total_price=total_price,
        is_paid=False,
        delivery_method=delivery_method,
        payment_method=payment_type,
    )

    items = []
    for cart_item in cart_items:
        print(f"✅ API Cart item: {cart_item.product.title}, qty: {cart_item.quantity}")
        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            price=cart_item.product.get_discounted_price(),
            quantity=cart_item.quantity,
            title=cart_item.product.title,
            discount=cart_item.product.discount,
            total_price=cart_item.product.get_discounted_price() * cart_item.quantity,  # Додаємо total_price
            price_snapshot=cart_item.product.get_discounted_price(),  # Додаємо price_snapshot
            discount_snapshot=cart_item.product.discount,  # Додаємо discount_snapshot
            user=request.user
        )
        items.append({
            'product': cart_item.product.title,
            'price': float(cart_item.product.get_discounted_price()),
            'quantity': cart_item.quantity,
        })

    if payment_type == "stripe-payment":
        session_data = {
            'mode': 'payment',
            'success_url': request.build_absolute_uri(reverse('payment:payment-success')),
            'cancel_url': request.build_absolute_uri(reverse('payment:payment-fail')),
            'line_items': [
                {
                    'price_data': {
                        'unit_amount': int(item['price'] * Decimal(100)),
                        'currency': 'usd',
                        'product_data': {'name': item['product']},
                    },
                    'quantity': item['quantity'],
                } for item in items
            ],
            'client_reference_id': str(order.id),
        }
        session = stripe.checkout.Session.create(**session_data)
        cart.cart_items.all().delete()
        return Response({'payment_url': session.url}, status=status.HTTP_201_CREATED)

    elif payment_type == "yookassa-payment":
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create({
            "amount": {"value": str(total_price * 93), "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(reverse('payment:payment-success')),
            },
            "capture": True,
            "test": True,
            "description": "Замовлення в магазині",
            "metadata": {"order_id": str(order.id)},
        }, idempotence_key)
        cart.cart_items.all().delete()
        return Response({'payment_url': payment.confirmation.confirmation_url}, status=status.HTTP_201_CREATED)

    elif payment_type == "cash-on-delivery":
        cart.cart_items.all().delete()
        serializer = OrderSerializer(order)
        return Response({
            'message': 'Order created successfully',
            'order': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({'error': 'Unsupported payment type'}, status=status.HTTP_400_BAD_REQUEST)

def payment_success(request: HttpRequest):
    order_id = request.GET.get('order_id') or request.session.get('order_id')
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        order.is_paid = True
        order.save()
    for key in list(request.session.keys()):
        if key == 'session_key' or key.startswith('cart'):
            del request.session[key]
    return render(request, 'payment/payment_success.html')

def payment_fail(request: HttpRequest):
    return render(request, 'payment/payment_fail.html')

@staff_member_required
def admin_order_pdf(request: HttpRequest, order_id):
    try:
        order = Order.objects.select_related('user', 'shipping_address').get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order doesn't exist or not found")
    html = render_to_string('payment/order/pdf/pdf_invoice.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f"filename=order_{order.id}.pdf"
    css_path = static('payment/css/pdf.css').lstrip('/')
    stylesheets = [weasyprint.CSS(css_path)]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response

# Оновлення статусу оплати
@swagger_auto_schema(
    method='patch',
    operation_description="Update the payment status of an order (admin only).",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'is_paid': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Payment status (true for paid, false for unpaid)'),
        },
        required=['is_paid'],
        example={'is_paid': True}
    ),
    responses={
        200: openapi.Response('Payment status updated', OrderSerializer),
        400: 'Bad Request',
        404: 'Order not found'
    }
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_payment_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    is_paid = request.data.get('is_paid')
    if is_paid is None:
        return Response({'error': 'is_paid field is required'}, status=status.HTTP_400_BAD_REQUEST)

    order.is_paid = is_paid
    order.save()
    serializer = OrderSerializer(order)
    return Response({
        'message': 'Payment status updated successfully',
        'order': serializer.data
    }, status=status.HTTP_200_OK)

# Оновлення статусу замовлення
@swagger_auto_schema(
    method='patch',
    operation_description="Update the status of an order (admin only).",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['new', 'processing', 'delivered', 'cancelled'],
                description='New status of the order'
            ),
        },
        required=['status'],
        example={'status': 'processing'}
    ),
    responses={
        200: openapi.Response('Order status updated', OrderSerializer),
        400: 'Invalid status value',
        404: 'Order not found'
    }
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    status_value = request.data.get('status')
    if status_value not in dict(Order.STATUS_CHOICES):
        return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

    order.status = status_value
    order.save()
    serializer = OrderSerializer(order)
    return Response({
        'message': 'Order status updated successfully',
        'order': serializer.data
    }, status=status.HTTP_200_OK)

# Скасування замовлення
@swagger_auto_schema(
    method='patch',
    operation_description="Cancel an order (admin only). Sets status to 'cancelled'.",
    request_body=None,
    responses={
        200: openapi.Response('Order cancelled', OrderSerializer),
        400: 'Order is already cancelled',
        404: 'Order not found'
    }
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    if order.status == 'cancelled':
        return Response({'error': 'Order is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'cancelled'
    order.save()
    serializer = OrderSerializer(order)
    return Response({
        'message': 'Order cancelled successfully',
        'order': serializer.data
    }, status=status.HTTP_200_OK)

# Видалення товару з замовлення
@swagger_auto_schema(
    method='delete',
    operation_description="Remove an item from an order (admin only).",
    responses={
        200: openapi.Response('Item removed', OrderSerializer),
        404: 'Order or item not found'
    }
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_order_item(request, order_id, item_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        order_item = OrderItem.objects.get(id=item_id, order=order)
    except OrderItem.DoesNotExist:
        return Response({'error': 'Order item not found'}, status=status.HTTP_404_NOT_FOUND)

    order_item.delete()
    order.total_price = sum(item.get_cost() for item in order.items.all())
    order.save()
    serializer = OrderSerializer(order)
    return Response({
        'message': 'Order item removed successfully',
        'order': serializer.data
    }, status=status.HTTP_200_OK)

# Додавання товару до замовлення
@swagger_auto_schema(
    method='post',
    operation_description="Add a new item to an order (admin only).",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the product to add'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of the product (default: 1)'),
        },
        required=['product_id'],
        example={'product_id': 828488, 'quantity': 3}
    ),
    responses={
        201: openapi.Response('Item added', OrderSerializer),
        400: 'Invalid product_id or quantity',
        404: 'Order or product not found'
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_order_item(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    if not product_id:
        return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return Response({'error': 'Quantity must be a positive integer'}, status=status.HTTP_400_BAD_REQUEST)

    order_item = OrderItem.objects.create(
        order=order,
        product=product,
        price=product.get_discounted_price(),
        quantity=quantity,
        title=product.title,
        discount=product.discount,
        total_price=product.get_discounted_price() * quantity,
        price_snapshot=product.get_discounted_price(),
        discount_snapshot=product.discount,
        user=order.user
    )
    order.total_price = sum(item.get_cost() for item in order.items.all())
    order.save()
    serializer = OrderSerializer(order)
    return Response({
        'message': 'Order item added successfully',
        'order': serializer.data
    }, status=status.HTTP_201_CREATED)