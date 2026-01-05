from django.contrib import admin
from django.utils.html import format_html
from .models import Product, FarmersBoxPreference

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_thumbnail', 'base_price_per_kg', 'active', 'seasonal_occasional']
    list_filter = ['active', 'seasonal_occasional']
    search_fields = ['name']
    list_editable = ['active']
    fields = ['name', 'description', 'image', 'image_preview', 'base_price_per_kg', 'minimum_order_kg', 'active', 'seasonal_occasional']
    readonly_fields = ['image_preview']
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_thumbnail.short_description = 'Image'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="margin-top: 10px;" />', obj.image.url)
        return "No image uploaded"
    image_preview.short_description = 'Current Image'

@admin.register(FarmersBoxPreference)
class FarmersBoxPreferenceAdmin(admin.ModelAdmin):
    list_display = ['client', 'product', 'preference']
    list_filter = ['preference', 'product']
    search_fields = ['client__business_name']