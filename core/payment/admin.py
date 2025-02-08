import csv
import datetime
from typing import Any

from django.contrib import admin
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Order, OrderItem, ShippingAddress


def export_paid_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f"attachment; fileaname=Paid{opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        if not getattr(obj, "is_paid"):
            continue
        
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return response

export_paid_to_csv.short_description = "Export Paid to CSV"


def export_not_paid_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename=NotPaid{opts.verbose_name}.csv"
    respose = HttpResponse(content_type="text/csv")
    respose["Content-Dispostion"] = content_disposition
    writer = csv.writer(respose)
    fields = [
        field 
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        if getattr(obj, "is_paid"):
            continue
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return respose


export_not_paid_to_csv.short_description = "Export Not Paid to CSV"


def order_pdf(obj):
    url = reverse('payment:admin-order-pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')

order_pdf.short_description = 'Invoice'


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name_bold', 'user', 'email', 'country', 'city', 'zip_code')
    empty_value_display = "-empty-"
    list_display_links = ('full_name_bold',)
    list_filter = ('user', 'country', 'city')

    @admin.display(description="Full Name", empty_value="Noname")
    def full_name_bold(self, obj):
        return format_html("<b style='font-weight: bold;'>{}</b>", obj.full_name)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    
    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if obj:
            return ['price', 'product', 'quantity', 'user']
        return super().get_readonly_fields(request, obj)

'''
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'shipping_address', 
        'total_price', 'created_at', 'updated_at', 
        'is_paid', 'discount', order_pdf
    ]
    list_filter = ['is_paid', 'updated_at', 'created_at',]
    inlines = [OrderItemInline]
    list_per_page = 15
    list_display_links = ['id', 'user']
    actions = [export_paid_to_csv, export_not_paid_to_csv]
'''


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'is_paid', 'delivery_method']
    list_filter = ['is_paid', 'delivery_method']
    search_fields = ['user__username', 'shipping_address__full_name']
    ordering = ['-created_at']
    
    # Додаємо випадаючий список у формі адміністратора
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "delivery_method":
            kwargs["choices"] = [
                ('nova_poshta', 'Nova Poshta'),
                ('ukrposhta', 'Ukrposhta'),
                ('courier', 'Courier'),
                ('self_pickup', 'Self Pickup'),
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
