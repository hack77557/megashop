'''
# core/cart/api_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemSerializer

from rest_framework.permissions import AllowAny  # Імпортуємо AllowAny


class CartDetailAPIView(APIView):
    """
    Отримання деталей кошика поточного користувача.
    Якщо кошик не існує, він буде створений.
    """
    permission_classes = [IsAuthenticated]
    #permission_classes = [AllowAny]  # Дозволяємо доступ всім на час тестування

    def get(self, request, *args, **kwargs):
        # Отримуємо або створюємо кошик для поточного користувача
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddToCartAPIView(APIView):
    """
    Додавання продукту до кошика.
    Очікується, що в POST-запиті передаються:
      - product_id: ідентифікатор продукту
      - quantity: кількість (за замовчуванням 1)
    """
    permission_classes = [IsAuthenticated]
    #permission_classes = [AllowAny]  # Дозволяємо доступ всім на час тестування

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'error': 'Потрібно вказати product_id.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Якщо продукт вже є в кошику – збільшуємо кількість
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateCartItemAPIView(APIView):
    """
    Оновлення кількості продукту в кошику.
    В URL передається item_id, а в запиті - нове значення quantity.
    """
    permission_classes = [IsAuthenticated]
    #permission_classes = [AllowAny]  # Дозволяємо доступ всім на час тестування

    def put(self, request, item_id, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {'error': 'Потрібно вказати кількість (quantity).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': 'Кількість має бути більше 0.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Неправильне значення кількості.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RemoveCartItemAPIView(APIView):
    """
    Видалення певного товару з кошика за його item_id.
    """
    permission_classes = [IsAuthenticated]
    #permission_classes = [AllowAny]  # Дозволяємо доступ всім на час тестування

    def delete(self, request, item_id, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ClearCartAPIView(APIView):
    """
    Повне очищення кошика користувача.
    """
    permission_classes = [IsAuthenticated]
    #permission_classes = [AllowAny]  # Дозволяємо доступ всім на час тестування

    def delete(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        # Припускаємо, що в моделі Cart є related_name='cart_items' для зв'язку з CartItem
        cart.cart_items.all().delete()
        return Response({'message': 'Кошик очищено.'}, status=status.HTTP_204_NO_CONTENT)
'''

# core/cart/api_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from shop.models import ProductProxy as Product
from .serializers import CartSerializer, CartItemSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class CartDetailAPIView(APIView):
    """
    Отримання деталей кошика поточного користувача.
    Якщо кошик не існує, він буде створений.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Отримання деталей кошика",
        operation_description="Отримання деталей кошика поточного користувача. Якщо кошик не існує, він буде створений.",
        responses={200: CartSerializer()}
    )
    def get(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
'''
class AddToCartAPIView(APIView):
    """
    Додавання продукту до кошика.
    """
    permission_classes = [IsAuthenticated]

    # Схема для тіла запиту
    request_body_schema = openapi.Schema(
         type=openapi.TYPE_OBJECT,
         required=["product_id"],
         properties={
             "product_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Ідентифікатор продукту"),
             "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, description="Кількість продукту", default=1)
         },
    )

    @swagger_auto_schema(
        operation_summary="Додавання продукту до кошика",
        operation_description="Додавання продукту до кошика. Очікується, що в POST-запиті передаються: product_id та quantity.",
        request_body=request_body_schema,
        responses={201: CartItemSerializer()}
    )
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'error': 'Потрібно вказати product_id.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
'''
class AddToCartAPIView(APIView):
    """
    Додавання продукту до кошика.
    """
    permission_classes = [IsAuthenticated]

    # Схема для тіла запиту
    request_body_schema = openapi.Schema(
         type=openapi.TYPE_OBJECT,
         required=["product_id"],
         properties={
             "product_id": openapi.Schema(
                 type=openapi.TYPE_INTEGER, 
                 description="Ідентифікатор продукту"
             ),
             "quantity": openapi.Schema(
                 type=openapi.TYPE_INTEGER, 
                 description="Кількість продукту", 
                 default=1
             )
         },
    )

    @swagger_auto_schema(
        operation_summary="Додавання продукту до кошика",
        operation_description="Додавання продукту до кошика. Очікується, що в POST-запиті передаються: product_id та quantity.",
        request_body=request_body_schema,
        responses={201: CartItemSerializer()}
    )
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'error': 'Потрібно вказати product_id.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Спробуємо привести product_id до цілого числа
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Невірний формат product_id.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Товар не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateCartItemAPIView(APIView):
    """
    Оновлення кількості продукту в кошику.
    """
    permission_classes = [IsAuthenticated]

    # Схема для тіла запиту
    request_body_schema = openapi.Schema(
         type=openapi.TYPE_OBJECT,
         required=["quantity"],
         properties={
             "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, description="Нова кількість", default=1)
         }
    )

    @swagger_auto_schema(
        operation_summary="Оновлення кількості продукту в кошику",
        operation_description="Оновлення кількості продукту в кошику. В URL передається item_id, а в запиті — нове значення quantity.",
        manual_parameters=[
            openapi.Parameter('item_id', openapi.IN_PATH, description="ID елемента кошика", type=openapi.TYPE_INTEGER)
        ],
        request_body=request_body_schema,
        responses={200: CartItemSerializer()}
    )
    def put(self, request, item_id, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {'error': 'Потрібно вказати кількість (quantity).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': 'Кількість має бути більше 0.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Неправильне значення кількості.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RemoveCartItemAPIView(APIView):
    """
    Видалення певного товару з кошика.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Видалення товару з кошика",
        operation_description="Видалення певного товару з кошика за його item_id.",
        manual_parameters=[
            openapi.Parameter('item_id', openapi.IN_PATH, description="ID елемента кошика", type=openapi.TYPE_INTEGER)
        ],
        responses={204: "Товар видалено."}
    )
    def delete(self, request, item_id, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ClearCartAPIView(APIView):
    """
    Повне очищення кошика користувача.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Очищення кошика",
        operation_description="Повне очищення кошика користувача.",
        responses={204: "Кошик очищено."}
    )
    def delete(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart.cart_items.all().delete()
        return Response({'message': 'Кошик очищено.'}, status=status.HTTP_204_NO_CONTENT)
