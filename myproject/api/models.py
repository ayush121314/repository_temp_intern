from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()  # Change to FloatField for item price
    stock = models.IntegerField()

    def __str__(self):
        return self.name
    
class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('success', 'Success'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('Item')  # ManyToMany relationship to Item
    total = models.FloatField(default=0.00)  # Change to FloatField for total
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=10, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
