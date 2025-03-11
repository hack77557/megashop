'''
# serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Додаємо додаткові дані до токена
        token['email'] = user.email
        token['middle_name'] = user.middle_name
        token['phone'] = user.phone
        token['date_of_birth'] = str(user.date_of_birth) if user.date_of_birth else None
        token['sex'] = user.sex
        token['language'] = user.language
        return token
'''


from djoser.serializers import UserSerializer
from rest_framework import serializers
from account.models import CustomUser  # Імпортуємо вашу модель користувача

class CustomUserSerializer(UserSerializer):
    """
    Кастомний серіалізатор для /account/api/users/me/, який додає всі поля користувача.
    """

    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    sex = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    language = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = (
            "id", "username", "email", "role", "first_name", "last_name", "middle_name", 
            "phone", "date_of_birth", "sex", "language", "is_staff", "is_active", "date_joined"
        )
        ref_name = "AccountCustomUserSerializer"  # 🔹 Додаємо унікальне ім'я
