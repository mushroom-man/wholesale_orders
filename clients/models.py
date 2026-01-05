from django.db import models

class Client(models.Model):
    DELIVERY_CHOICES = [
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]
    
    STATE_CHOICES = [
        ('VIC', 'Victoria'),
        ('NSW', 'New South Wales'),
        ('QLD', 'Queensland'),
        ('SA', 'South Australia'),
        ('WA', 'Western Australia'),
        ('TAS', 'Tasmania'),
        ('NT', 'Northern Territory'),
        ('ACT', 'Australian Capital Territory'),
    ]
    
    business_name = models.CharField(max_length=200)
    login_email = models.EmailField(unique=True)
    delivery_day = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    street_address = models.CharField(max_length=200)
    street_address_2 = models.CharField(max_length=200, blank=True)
    suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=3, choices=STATE_CHOICES)
    postcode = models.CharField(max_length=4)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.business_name


class Contact(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.client.business_name})"
