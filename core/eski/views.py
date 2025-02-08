import requests
import os
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet

# Імпортуємо моделі з shop та payment
from shop.models import Category, Product, Attribute
from payment.models import Order, OrderItem
from shop.serializers import ProductSerializer, ProductDetailtSerializer, AttributeSerializer

from .serializers import CategorySerializer, OrderSerializer, OrderCreateSerializer#, ProductDetailtSerializer
#from rest_framework.renderers import JSONRenderer
from django.shortcuts import get_object_or_404


# URLs для проксування
#SHOP_API_BASE_URL = "http://192.168.163.10:8000/shop/api"
SHOP_API_BASE_URL = os.getenv('SHOP_API_BASE_URL', 'http://localhost:8000/shop/api')

# Функція для отримання токенів
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Проксування запитів до shop API
class ProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, endpoint):
        response = requests.get(f"{SHOP_API_BASE_URL}/{endpoint}/", headers={'Authorization': request.headers.get('Authorization')})
        return JsonResponse(response.json(), safe=False)

    def post(self, request, endpoint):
        response = requests.post(f"{SHOP_API_BASE_URL}/{endpoint}/", json=request.data, headers={'Authorization': request.headers.get('Authorization')})
        return JsonResponse(response.json(), safe=False, status=response.status_code)

    def put(self, request, endpoint, pk):
        response = requests.put(f"{SHOP_API_BASE_URL}/{endpoint}/{pk}/", json=request.data, headers={'Authorization': request.headers.get('Authorization')})
        return JsonResponse(response.json(), safe=False, status=response.status_code)

    def delete(self, request, endpoint, pk):
        response = requests.delete(f"{SHOP_API_BASE_URL}/{endpoint}/{pk}/", headers={'Authorization': request.headers.get('Authorization')})
        return JsonResponse(response.json(), safe=False, status=response.status_code)

# Аутентифікація через JWT (HttpOnly cookies)
class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            tokens = get_tokens_for_user(user)
            response = JsonResponse({'message': 'Login successful'})
            response.set_cookie('access_token', tokens['access'], httponly=True)
            return response
        return Response({'error': 'Invalid credentials'}, status=400)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        response = JsonResponse({'message': 'Logged out'})
        response.delete_cookie('access_token')
        return response

# Використання існуючих моделей
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None  # Вимикаємо пагінацію для категорій
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

'''     ДОБРЕ РОБОЧИЙ ВАРІАНТ!!!!!!!!!!!!!!!!!!!!!!!!
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('product_attributes__attribute')  # Додаємо prefetch_related
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailtSerializer  # Використовуйте оригінальну назву
        return ProductSerializer
'''
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('product_attributes__attribute')  # Додаємо prefetch_related
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailtSerializer  # Використовуйте оригінальну назву
        return ProductSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']  # Додаємо можливість фільтрації за категорією
    search_fields = ['title', 'brand']  # Можливість пошуку за назвою та брендом
    ordering_fields = ['price', 'created_at']  # Сортування за ціною або датою створення
'''
    # ВИМКНЕННЯ РЕНДЕРИНГУ HTML-ФОРМ
    def get_renderers(self):
        """Вимикаємо HTML рендерери, залишаємо тільки JSON"""
        return [JSONRenderer()]
'''
'''
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
'''
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    #permission_classes = [permissions.IsAuthenticated]
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """
        Отримати всі товари в конкретному замовленні.
        """
        order = get_object_or_404(Order, pk=pk, user=request.user)
        items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)


'''
class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = ProductAttributeSerializer
'''
class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer  # Використовуємо правильний серіалізатор
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]


# користувач
from django.contrib.auth import get_user_model
User = get_user_model()
#from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerializer
#from rest_framework.permissions import IsAuthenticated, IsAdminUser
#from rest_framework.decorators import action
#from rest_framework.response import Response

class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("id")  # Сортування за id
    serializer_class = UserSerializer

    def get_permissions(self):
        """Адміни можуть бачити всіх, а користувачі - тільки себе"""
        if self.action == 'list':
            return [IsAdminUser()]  # Тільки адміни можуть бачити список користувачів
        return [IsAuthenticated()]  # Інші можуть працювати тільки зі своїм профілем

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Повертає дані про поточного користувача"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    

# користувач новий тест додаткові поля 