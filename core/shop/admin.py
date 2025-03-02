from django.contrib import admin

from .models import Category, Product, ProductAttribute###############

# type hinting imports
from django.http import HttpRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category Model Admin
    """
    list_display = ('name', 'parent', 'slug', 'description')
    ordering = ('name',)
    
    def  get_prepopulated_fields(self, request: HttpRequest, obj=None) -> dict:
        """Returns a dictionary of fields to pre-populate from the request."""
        return {
            'slug': ('name',),
        }
##################################################################################    
from django.contrib import admin
from .models import Product, Attribute, ProductAttribute

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    search_fields = ['name']

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1 # Кількість порожніх рядків для додавання нових характеристик
    autocomplete_fields = ['attribute']  # Дозволяє автозаповнення існуючих характеристик

##################################################################################

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product Model Admin
    """
    list_display = ('title', 'brand', 'price', 'discount', 'available', 'created_at', 'updated_at', 'product_code')
    list_filter = ('available', 'created_at', 'updated_at')
    ordering = ('title',)
    inlines = [ProductAttributeInline]  # Додаємо характеристики до сторінки товару ##################################################################################

    def  get_prepopulated_fields(self, request: HttpRequest, obj=None) -> dict:
        """Returns a dictionary of fields to pre-populate from the request."""
        return {
            'slug': ('title',),
        }
    

