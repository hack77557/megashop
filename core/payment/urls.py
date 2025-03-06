from django.urls import path

from . import views
from .webhooks import stripe_webhook, yookassa_webhook

app_name = 'payment'

urlpatterns = [
    # HTML-інтерфейс
    path("shipping/", views.shipping_view, name="shipping"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("complete-order/", views.complete_order, name="complete-order"),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('payment-fail/', views.payment_fail, name='payment-fail'),
    # Webhooks
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    path('webhook-yookassa/', yookassa_webhook, name='webhook-yookassa'),
    # Order PDF
    path("order/<int:order_id>/pdf/", views.admin_order_pdf, name="admin-order-pdf"),
    # API-ендпоінт для оформлення замовлення
    path("api/complete-order/", views.api_complete_order, name="api-complete-order"),
    path('api/admin/order/<int:order_id>/update-payment-status/', views.update_payment_status, name='update_payment_status'),
    path('api/admin/order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('api/admin/order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('api/admin/order/<int:order_id>/remove-item/<int:item_id>/', views.remove_order_item, name='remove_order_item'),
    path('api/admin/order/<int:order_id>/add-item/', views.add_order_item, name='add_order_item'),
]
