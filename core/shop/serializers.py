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

        #print("Received attributes_data:", attributes_data)  # 🔥 Додаємо логування

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
        attributes_data = request.data.get("attributes", [])  # Отримуємо атрибути
        images_data = request.FILES.getlist("images", [])  # Отримуємо файли

        print("🟢 Тип attributes_data:", type(attributes_data))
        print("🟢 Отримані атрибути (attributes_data):", attributes_data)
        print("🟢 Отримані файли (images_data):", images_data)

        # 🔥 Оновлення основних полів продукту
        instance = super().update(instance, validated_data)

        # 🔥 Переконуємося, що `attributes_data` є списком рядків
        if isinstance(attributes_data, str):
            attributes_data = [attributes_data]  # Якщо передано як рядок, перетворюємо в список

        if not isinstance(attributes_data, list):
            print(f"❌ Очікувався список, отримано: {type(attributes_data)}")
            return instance  # Якщо дані некоректні, не оновлюємо атрибути

        # 🔥 Оновлення атрибутів
        instance.product_attributes.all().delete()  # Видаляємо старі атрибути

        for attr in attributes_data:
            print(f"🔹 Обробка атрибута: {attr}")

            if not isinstance(attr, str):
                print(f"⚠️ Пропущено некоректний атрибут (очікується рядок): {attr}")
                continue

            attr = attr.strip()
            if ":" not in attr:
                print(f"⚠️ Пропущено некоректний формат атрибута (очікується 'Назва: Значення'): {attr}")
                continue

            try:
                attribute_name, value = attr.split(":", 1)
                attribute_name, value = attribute_name.strip(), value.strip()
            except ValueError:
                print(f"⚠️ Помилка при розділенні атрибута: {attr}")
                continue

            if not attribute_name or not value:
                print(f"⚠️ Пропущені значення для атрибута: {attr}")
                continue

            # 🔥 Якщо атрибут існує → використовуємо його, якщо ні → створюємо
            attribute, _ = Attribute.objects.get_or_create(name=attribute_name)
            ProductAttribute.objects.create(product=instance, attribute=attribute, value=value)

            print(f"✅ Збережено атрибут: {attribute_name} = {value}")

        return instance
'''
    def update(self, instance, validated_data):
        """ Оновлення продукту разом із атрибутами та зображеннями """
        request = self.context.get('request')  # Отримуємо request
        attributes_data = request.data.get('attributes', [])  # Отримуємо атрибути у форматі списку
        images_data = request.FILES.getlist('images', [])  # Отримуємо файли

        # 🔥 Оновлення основних полів продукту
        instance = super().update(instance, validated_data)

        # 🔥 Оновлення атрибутів
        if attributes_data:
            instance.product_attributes.all().delete()  # Видаляємо старі атрибути
            for attr in attributes_data:
                attribute_name = attr.get('attribute')
                value = attr.get('value')

                if not attribute_name or not value:
                    continue  # Пропускаємо помилкові дані

                # 🔥 Якщо атрибут існує → використовуємо його, якщо ні → створюємо
                attribute, _ = Attribute.objects.get_or_create(name=attribute_name.strip())
                ProductAttribute.objects.create(product=instance, attribute=attribute, value=value.strip())

        # 🔥 Оновлення зображень
        if images_data:
            instance.images.all().delete()  # Видаляємо старі зображення
            for image in images_data:
                ProductImage.objects.create(product=instance, image=image)

        return instance
'''

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



