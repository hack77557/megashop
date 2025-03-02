from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, OrderViewSet, AuthViewSet, ProxyView, AttributeViewSet, UserViewSet#, ProductImageViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
#router.register(r'discounts', DiscountViewSet)
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'attributes', AttributeViewSet)
router.register(r'users', UserViewSet)

#router.register(r'product-images', ProductImageViewSet, basename='product-images')

urlpatterns = [
    path('', include(router.urls)),
    path('<str:endpoint>/', ProxyView.as_view(), name='proxy-endpoint'),
    path('<str:endpoint>/<int:pk>/', ProxyView.as_view(), name='proxy-detail-endpoint'),
]
