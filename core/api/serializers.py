from django.contrib.auth import get_user_model
from rest_framework import serializers

from recommend.models import Review
from shop.models import Category, Product

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = serializers.SlugRelatedField(
        many=False,
        slug_field="name",
        queryset=Category.objects.all(),
    )
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'brand', 'image', 'price', 'category', 'created_at', 'updated_at']
        ref_name = "API_Product"  # Унікальне ім'я для цього серіалізатора


class ReviewSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(
        many=False,
        read_only=True,
    )
        
    class Meta:
        model = Review
        fields = ['id', 'rating', 'content', 'created_by', 'created_at', 'product_id']
        read_only_fields = ['id', 'created_by', 'created_at']


class ProductDetailtSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = serializers.SlugRelatedField(
        many=False,
        slug_field="name",
        queryset=Category.objects.all(),
    )
    discounted_price = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "brand", "category", "price", 
            "image", "available", "discount", "created_at", 
            "updated_at", "discounted_price", "reviews"
        ]
        ref_name = "APIProductDetailSerializer"  # Унікальне ім'я
    
    
    def get_discounted_price(self, obj):
        discounted_price = obj.get_discounted_price()
        return str(discounted_price)


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Встановлюємо атрибут swagger_schema для поля password після створення поля
        self.fields['password'].swagger_schema = {'type': 'string', 'format': 'password'}

    def create(self, validated_data):
        email = validated_data['email']
        username = email.split('@')[0]
        user = User(email=email, username=username)
        user.set_password(validated_data['password'])
        user.save()
        return user

'''
#####
from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'children']

    def get_children(self, obj):
        """Рекурсивно отримує дочірні категорії."""
        children = obj.children.all()
        return CategorySerializer(children, many=True).data
'''

from djoser.serializers import UserSerializer

class DjoserCustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        ref_name = "DjoserUser"  # Це унікальне ім'я, щоб не було конфлікту у Swagger