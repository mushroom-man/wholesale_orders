from django.contrib import admin
from .models import (
    StandingOrder, StandingOrderLine, StandingOrderHistory,
    Order, OrderLine, OrderLineFulfilment, OrderHistory
)

class StandingOrderLineInline(admin.TabularInline):
    model = StandingOrderLine
    extra = 1

class StandingOrderHistoryInline(admin.TabularInline):
    model = StandingOrderHistory
    extra = 0
    readonly_fields = ['changed_at', 'changed_by', 'change_type', 'details']
    can_delete = False

@admin.register(StandingOrder)
class StandingOrderAdmin(admin.ModelAdmin):
    list_display = ['client', 'start_date', 'end_date', 'active', 'priority']
    list_filter = ['active', 'client__delivery_day']
    search_fields = ['client__business_name']
    inlines = [StandingOrderLineInline, StandingOrderHistoryInline]

class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 1

class OrderHistoryInline(admin.TabularInline):
    model = OrderHistory
    extra = 0
    readonly_fields = ['changed_at', 'changed_by', 'change_type', 'details']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['client', 'delivery_date', 'order_type', 'status', 'total_kg', 'total_price']
    list_filter = ['status', 'order_type', 'delivery_date', 'client__delivery_day']
    search_fields = ['client__business_name']
    list_editable = ['status']
    inlines = [OrderLineInline, OrderHistoryInline]
    readonly_fields = ['placed_at', 'confirmed_at']

@admin.register(OrderLineFulfilment)
class OrderLineFulfilmentAdmin(admin.ModelAdmin):
    list_display = ['order_line', 'product', 'quantity_kg']
    search_fields = ['order_line__order__client__business_name', 'product__name']
