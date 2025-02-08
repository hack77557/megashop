from drf_yasg.inspectors import FieldInspector
from drf_yasg import openapi
from rest_framework.fields import CharField

class PasswordFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        # Перевіряємо, чи це CharField і в ньому встановлено стиль input_type == 'password'
        if isinstance(obj, CharField) and obj.style.get('input_type') == 'password':
            return openapi.Schema(type=openapi.TYPE_STRING, format='password')
        return result
from drf_yasg.inspectors import FieldInspector
from drf_yasg import openapi
from rest_framework.fields import ReadOnlyField

class ReadOnlyFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(obj, ReadOnlyField):
            # Наприклад, повертаємо тип string
            return openapi.Schema(type=openapi.TYPE_STRING)
        return result
from drf_yasg.inspectors import FieldInspector
from drf_yasg import openapi
from rest_framework.relations import PrimaryKeyRelatedField

class PrimaryKeyRelatedFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(obj, PrimaryKeyRelatedField):
            # Припустимо, що ключ – ціле число
            return openapi.Schema(type=openapi.TYPE_INTEGER)
        return result
from drf_yasg.inspectors import FieldInspector
from drf_yasg import openapi
from rest_framework.fields import ChoiceField

class ChoiceFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(obj, ChoiceField):
            # Повертаємо рядок із переліком можливих значень
            return openapi.Schema(type=openapi.TYPE_STRING, enum=list(obj.choices.keys()))
        return result
from drf_yasg.inspectors import FieldInspector
from drf_yasg import openapi
from rest_framework.fields import EmailField

class EmailFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(obj, EmailField):
            return openapi.Schema(type=openapi.TYPE_STRING, format='email')
        return result
from drf_yasg.inspectors import FieldInspector
from drf_yasg import openapi
from rest_framework.serializers import SerializerMethodField

class SerializerMethodFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(obj, SerializerMethodField):
            # Можна задокументувати як string або тип, який підходить для вашої логіки
            return openapi.Schema(type=openapi.TYPE_STRING)
        return result
