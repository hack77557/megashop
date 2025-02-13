from drf_yasg.inspectors import SwaggerAutoSchema
from api.swagger_inspectors import (
    PasswordFieldInspector, ReadOnlyFieldInspector,
    PrimaryKeyRelatedFieldInspector, ChoiceFieldInspector,
    EmailFieldInspector, SerializerMethodFieldInspector
)

class CustomAutoSchema(SwaggerAutoSchema):
    field_inspectors = [
        PasswordFieldInspector,
        ReadOnlyFieldInspector,
        PrimaryKeyRelatedFieldInspector,
        ChoiceFieldInspector,
        EmailFieldInspector,
        SerializerMethodFieldInspector,
    ] + SwaggerAutoSchema.field_inspectors



