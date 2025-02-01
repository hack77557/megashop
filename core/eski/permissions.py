from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsAdminOrReadOnly(BasePermission):
    """
    Дозвіл, який дозволяє лише адміністраторам змінювати дані,
    а всім користувачам - тільки читати.
    """
    def has_permission(self, request, view) -> bool:
        # Дозволяє читання всім
        if request.method in SAFE_METHODS:
            return True
        # Дозволяє зміну тільки адміністраторам
        return request.user and request.user.is_staff
