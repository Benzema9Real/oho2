from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
class Color(models.Model):
    name = models.CharField(max_length=50)
    rgb = models.CharField(max_length=7, help_text="Введите в формате #RRGGBB")

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)  # Например 10 = 10%
    colors = models.ManyToManyField(Color, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    is_new = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def discounted_price(self):
        discount = Decimal(self.discount_percent) / Decimal(100)
        return self.price * (Decimal(1) - discount)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"{self.product.name} image"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')