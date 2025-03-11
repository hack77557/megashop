
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from . import views

######
#from django.urls import path
#from .views import CategoryListView, CategoryDetailView
######

from rest_framework.permissions import AllowAny
from django.urls import path

from django.urls import path, re_path
from rest_framework import permissions

from django.urls import path
from django.http import JsonResponse
from django.middleware.csrf import get_token

def get_csrf_token(request):
    response = JsonResponse({"csrfToken": get_token(request)})
    response["X-CSRFToken"] = get_token(request)
    return response


app_name = 'api'

schema_view = get_schema_view(
    openapi.Info(
        title="Anime & Game E-commerce API",
        default_version="v1",
        description="Anime & Game E-commerce API description...",
        terms_of_service="https://example.com/terms/",
        contact=openapi.Contact(email="administrator@ecommerce.django"),
        license=openapi.License(name="MIT License"),
    ),
    #public=True,
    #permission_classes=(AllowAny,),
    public=True,
    #permission_classes=(permissions.AllowAny,),
    permission_classes=[AllowAny],
)


urlpatterns = [
    # Products
    #path("products/", views.ProductListAPIView.as_view()),
    path("products/<int:pk>/", views.ProductDetailAPIView.as_view()),
    # Reviews
    path("reviews/create/", views.ReviewCreateAPIView.as_view()),
    # User
    path("auth/", include('djoser.urls')),
    path("auth/", include('djoser.urls.jwt')),
    # Docs
    path(
        "swagger/", 
        schema_view.with_ui('swagger', cache_timeout=0), 
        name="schema-swagger-ui"
    ),
    path(
        "redoc/", 
        schema_view.with_ui('redoc', cache_timeout=0), 
        name="schema-redoc"
    ),
    # інші
    #path('shop/', include('shop.urls', namespace='shop')),
    #path('categories/', CategoryListView.as_view(), name='category-list'),
    #path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('csrf/', get_csrf_token, name='get-csrf-token'),  # ✅ Додаємо ендпоінт для CSRF


]
