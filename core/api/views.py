from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Product
from recommend.models import Review

from .serializers import ProductSerializer, ProductDetailtSerializer, ReviewSerializer
from .permissions import IsAdminOrReadOnly
from .pagination import StandardResultsSetPagination


class ProductListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').order_by('id')


class ProductDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductDetailtSerializer
    lookup_field = "pk"

'''
class ReviewCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        product_id = self.request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        existing_review = Review.objects.filter(
            product=product, created_by=self.request.user).exists()
        if existing_review:
            raise ValidationError("You have already reviewed this product.")
            
        serializer.save(created_by=self.request.user, product=product)
'''
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ReviewCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    @swagger_auto_schema(
        operation_description="Додати відгук до продукту",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID продукту"
                ),
                'text': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Текст відгуку"
                ),
                'rating': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Оцінка (1-5)"
                )
            },
            required=['product_id', 'text', 'rating']
        ),
        responses={201: ReviewSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)






'''
Можна протестити на швидкодію
Якщо користувач надсилає багато запитів із тим самим product_id, це може викликати перевантаження бази даних або додаткові затримки.

Що зробити:

Логіку перевірки можна оптимізувати, зменшивши кількість запитів до бази

    def perform_create(self, serializer):
        product_id = self.request.data.get('product_id')
        if not Product.objects.filter(id=product_id).exists():
            raise ValidationError("Product does not exist.")
        
        if Review.objects.filter(product_id=product_id, created_by=self.request.user).exists():
            raise ValidationError("You have already reviewed this product.")

        serializer.save(created_by=self.request.user, product_id=product_id)
'''


'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Category
from .serializers import CategorySerializer

class CategoryListView(ListAPIView):
    queryset = Category.objects.filter(parent=None)  # Тільки кореневі категорії
    serializer_class = CategorySerializer


class CategoryDetailView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
'''

'''
#########################################
from rest_framework.generics import ListAPIView
from shop.models import Category
from api.serializers import CategorySerializer

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
'''


from rest_framework.permissions import IsAuthenticated

class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view!"})


from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.views import APIView

class GetCSRFTokenView(APIView):
    def get(self, request):
        response = JsonResponse({"csrfToken": get_token(request)})
        response["X-CSRFToken"] = get_token(request)  # Додаємо заголовок
        return response
    


from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API Documentation",
    ),
    public=True,  # ✅ Дозволяє доступ без авторизації
    permission_classes=[AllowAny],  # ✅ Дозволяє всім переглядати Swagger
)