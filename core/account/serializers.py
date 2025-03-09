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