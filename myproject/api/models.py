from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('Item')  # Adjust if needed
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Ensure this field exists
    created_at = models.DateTimeField(auto_now_add=True)

