from rest_framework import serializers
from .models import Category, Product, ProductAttribute, Attribute, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  # Додаємо підтримку зображень

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'parent', 'image']  # Додаємо `image`
        ref_name = "ShopCategorySerializer"


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = serializers.CharField(source='attribute.name')

    class Meta:
        model = ProductAttribute
        fields = ['attribute', 'value']

    def to_internal_value(self, data):
        """
        Оскільки `multipart/form-data` не підтримує вкладені JSON-об'єкти, 
        цей метод перетворює вхідні дані у відповідний формат.
        """
        if isinstance(data, list):
            return super().to_internal_value({k: v for d in data for k, v in d.items()})
        return super().to_internal_value(data)
   

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        #fields = ['id', 'product', 'image']
        #extra_kwargs = {'product': {'required': False}}  # 🔥 `product` тепер не є обов'язковим
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(many=True, required=False)
    images = ProductImageSerializer(many=True, required=False)  # 🔥 Додаємо список зображень, Робимо поле `images` доступним для запису
    image = serializers.ImageField(required=False)  # 🔥 Головне зображення


    class Meta:
        model = Product
        fields = [
            'id', 'title', 'brand', 'description', 'slug', 'price', 'image', 'images', 'purchase_price', 'available', 'discount', 'category', 'attributes', 'product_code'
        ] 
        ref_name = "ShopProductSerializer"

    def create(self, validated_data):

        request = self.context.get('request')  # Отримуємо request
        #attributes_data = request.data.getlist('attributes')  # Отримуємо атрибути з `form-data`
        attributes_data = request.POST.getlist('attributes')
        images_data = request.FILES.getlist('images')  # Отримуємо файли

        # ✅ Додаємо логування POST-запиту
        #print("🟢 [POST] Отримано дані:")
        #print("    - validated_data:", validated_data)
        #print("    - attributes_data:", attributes_data)
        #print("    - images_data:", images_data)

        product = Product.objects.create(**validated_data)

         # 🔥 Обробка атрибутів
        for attr in attributes_data:
            try:
                attribute_name, value = attr.split(':', 1)  # Ділимо лише на 2 частини
                attribute, _ = Attribute.objects.get_or_create(name=attribute_name.strip())
                ProductAttribute.objects.create(product=product, attribute=attribute, value=value.strip())
            except ValueError:
                raise serializers.ValidationError(
                    {"attributes": "Невірний формат. Використовуйте 'Назва: Значення'."}
                )

        # Додаємо зображення
        for image_data in images_data:
            #ProductImage.objects.create(product=product, **image_data)  # 🔥 Додаємо зображення до продукту
            ProductImage.objects.create(product=product, image=image_data)

        return product

    def to_representation(self, instance):
        """
        Перевизначаємо відповідь, щоб коректно відображати вкладені дані `attributes` та `images`.
        """
        representation = super().to_representation(instance)

        # Додаємо атрибути до відповіді
        representation['attributes'] = ProductAttributeSerializer(instance.product_attributes.all(), many=True).data
        
        # Додаємо всі зображення до відповіді
        representation['images'] = ProductImageSerializer(instance.images.all(), many=True).data

        return representation
    
    def update(self, instance, validated_data):
        """ Оновлення продукту разом із атрибутами та зображеннями """
        request = self.context.get("request")  # Отримуємо request
        attributes_data = request.POST.getlist("attributes")  # Отримуємо атрибути
        images_data = request.FILES.getlist("images", [])  # Отримуємо файли

        #print(f"🔵 [PUT] Отримані атрибути: {attributes_data}")
        #print(f"🔵 [PUT] Отримані зображення: {images_data}")

        # 🔥 Оновлення основних полів продукту
        instance = super().update(instance, validated_data)

        # 🔥 Видаляємо старі атрибути
        instance.product_attributes.all().delete()

        for attr in attributes_data:
            print(f"🔹 [PUT] Обробка атрибута: {attr}")
            try:
                attribute_name, value = attr.split(":", 1)
                attribute, _ = Attribute.objects.get_or_create(name=attribute_name.strip())
                ProductAttribute.objects.create(product=instance, attribute=attribute, value=value.strip())
                print(f"✅ [PUT] Збережено атрибут: {attribute_name} = {value}")
            except ValueError:
                print(f"⚠️ [PUT] Помилка при обробці атрибута: {attr}")

        # 🔥 Оновлення зображень
        if images_data:
            instance.images.all().delete()
            for image in images_data:
                ProductImage.objects.create(product=instance, image=image)

        return instance
 


class ProductDetailtSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(source='product_attributes', many=True)  # Пов'язане поле
    images = ProductImageSerializer(many=True, required=False)  # Додаткові зображення

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'brand', 'description', 'slug', 'price', 'purchase_price', 'image', 'images', 'available',
            'created_at', 'updated_at', 'discount', 'category', 'attributes', 'product_code'
        ]
        ref_name = "ShopProductDetailSerializer"  # Унікальне ім'я

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']  # Використовуємо коректні поля



