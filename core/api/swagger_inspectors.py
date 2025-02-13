# api/swagger_inspectors.py
from drf_yasg import openapi
from drf_yasg.inspectors import FieldInspector
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

class PasswordFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if isinstance(field, serializers.CharField) and field.style.get('input_type') == 'password':
            return openapi.Schema(type=openapi.TYPE_STRING, format='password')
        return None

class ReadOnlyFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        # Якщо поле read_only, спробуємо "пробити" його за допомогою наступних інспекторів,
        # а потім позначимо як readOnly.
        if getattr(field, 'read_only', False):
            schema = self.probe_field(field, **kwargs)
            if schema is not None:
                schema.readOnly = True
                return schema
        return None

class PrimaryKeyRelatedFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if isinstance(field, PrimaryKeyRelatedField):
            return openapi.Schema(type=openapi.TYPE_INTEGER)
        return None

class ChoiceFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if hasattr(field, 'choices') and field.choices:
            enum = list(field.choices.keys())
            field_type = openapi.TYPE_INTEGER if isinstance(enum[0], int) else openapi.TYPE_STRING
            return openapi.Schema(type=field_type, enum=enum)
        return None

class EmailFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if isinstance(field, serializers.EmailField):
            return openapi.Schema(type=openapi.TYPE_STRING, format='email')
        return None

class SerializerMethodFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        if isinstance(field, serializers.SerializerMethodField):
            # За замовчуванням повертаємо string. При необхідності можете розширити логіку.
            return openapi.Schema(type=openapi.TYPE_STRING)
        return None
