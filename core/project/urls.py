from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

from django_email_verification import urls as email_urls



#from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls', namespace='shop')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('account/', include('account.urls', namespace='account')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('recommend/', include('recommend.urls', namespace='recommend')),
    path('email/', include(email_urls), name='email-verification'),  # FIXME: replace name to namespace
    path('api/v1/', include('api.urls', namespace='api')),

    path('eski/', include('eski.urls')),

    #path('api-auth/', include('rest_framework.urls')),  # <-- Ось тут API Admin
    #path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    #path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('', views.index_view, name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

