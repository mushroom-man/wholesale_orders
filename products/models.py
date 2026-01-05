from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    base_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)
    seasonal_occasional = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FarmersBoxPreference(models.Model):
    PREFERENCE_CHOICES = [
        ('prefer', 'Prefer'),
        ('exclude', 'Exclude'),
        ('no_preference', 'No Preference'),
    ]
    
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='farmers_box_preferences')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    preference = models.CharField(max_length=20, choices=PREFERENCE_CHOICES, default='no_preference')
    
    class Meta:
        unique_together = ['client', 'product']
    
    def __str__(self):
        return f"{self.client.business_name} - {self.product.name}: {self.preference}"