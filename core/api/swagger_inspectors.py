
from drf_yasg.inspectors import FieldInspector

class CustomFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, **kwargs):
        # Якщо поле write_only або має інші специфічні властивості, повертаємо явне визначення
        if getattr(field, 'write_only', False):
            # Наприклад, якщо це поле типу CharField з параметром input_type password:
            if hasattr(field, 'style') and field.style.get('input_type') == 'password':
                return {'type': 'string', 'format': 'password'}
        # Інакше повертаємо None, щоб продовжити стандартну обробку
        return None
