from django.contrib import admin
from .models import Client, Contact

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'delivery_day', 'suburb', 'state', 'active']
    list_filter = ['delivery_day', 'state', 'active']
    search_fields = ['business_name', 'suburb']
    inlines = [ContactInline]