''' Маршрутизація Django urls
from django.urls import path
from .views import cart_view, cart_add, cart_delete, cart_update, cart_clear

app_name = 'cart'

urlpatterns = [

    path('', cart_view, name='cart-view'),
    path('add/', cart_add, name='add-to-cart'),
    path('delete/', cart_delete, name='delete-from-cart'),
    path('update/', cart_update, name='update-cart'),
    path('clear/', cart_clear, name='clear-cart'),

]
'''
from django.urls import path
from .views import cart_view, cart_add, cart_delete, cart_update, cart_clear
from .api_views import (
    CartDetailAPIView,
    AddToCartAPIView,
    UpdateCartItemAPIView,
    RemoveCartItemAPIView,
    ClearCartAPIView
)

app_name = 'cart'

urlpatterns = [
    # API-ендпоінти, доступні за /cart/api/...
    path('api/', CartDetailAPIView.as_view(), name='api-cart-detail'),
    path('api/add/', AddToCartAPIView.as_view(), name='api-cart-add'),
    path('api/item/<int:item_id>/update/', UpdateCartItemAPIView.as_view(), name='api-cart-item-update'),
    path('api/item/<int:item_id>/remove/', RemoveCartItemAPIView.as_view(), name='api-cart-item-remove'),
    path('api/clear/', ClearCartAPIView.as_view(), name='api-cart-clear'),

    # Django звичайні view
    path('', cart_view, name='cart-view'),
    path('add/', cart_add, name='add-to-cart'),
    path('delete/', cart_delete, name='delete-from-cart'),
    path('update/', cart_update, name='update-cart'),
    path('clear/', cart_clear, name='clear-cart'),
]
