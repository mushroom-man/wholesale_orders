from django.db import models
from django.utils import timezone

class StandingOrder(models.Model):
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='standing_orders')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank for ongoing")
    active = models.BooleanField(default=True)
    priority = models.IntegerField(default=10, help_text="Lower number = higher priority when stock is short")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.client.business_name} - Standing Order"


class StandingOrderLine(models.Model):
    standing_order = models.ForeignKey(StandingOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name}: {self.quantity_kg} kg"


class StandingOrderHistory(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('created', 'Created'),
        ('modified', 'Modified'),
        ('paused', 'Paused'),
        ('resumed', 'Resumed'),
        ('ended', 'Ended'),
    ]
    
    standing_order = models.ForeignKey(StandingOrder, on_delete=models.CASCADE, related_name='history')
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=200)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    details = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Standing order histories"
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.standing_order} - {self.change_type} on {self.changed_at}"


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('adhoc', 'Ad-hoc'),
        ('standing', 'Standing'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('packed', 'Packed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='orders')
    delivery_date = models.DateField()
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='adhoc')
    standing_order = models.ForeignKey(StandingOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    placed_at = models.DateTimeField(auto_now_add=True)
    placed_by = models.CharField(max_length=200)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    total_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, help_text="Client notes")
    internal_notes = models.TextField(blank=True, help_text="Staff notes - not visible to client")
    
    class Meta:
        ordering = ['-delivery_date', '-placed_at']
    
    def __str__(self):
        return f"{self.client.business_name} - {self.delivery_date}"


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity_ordered_kg = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_delivered_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.product.name}: {self.quantity_ordered_kg} kg"


class OrderLineFulfilment(models.Model):
    """Tracks actual products in a Farmer's Box"""
    order_line = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name='fulfilment')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name}: {self.quantity_kg} kg"


class OrderHistory(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('created', 'Created'),
        ('modified', 'Modified'),
        ('cancelled', 'Cancelled'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=200)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    details = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Order histories"
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.order} - {self.change_type} on {self.changed_at}"
