from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Color(models.Model):
    name = models.CharField(max_length=50)
    hex = models.CharField(max_length=7, default='#000000', help_text="Формат: #RRGGBB")
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(default='', blank=True) # для URL: /catalog/sumki/

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)
    colors = models.ManyToManyField(Color, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_new = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def discounted_price(self):
        if self.discount_percent:
            discount = Decimal(self.discount_percent) / Decimal(100)
            result = self.price * (Decimal(1) - discount)
            return result.quantize(Decimal('0.01'))
        return self.price

    @property
    def has_discount(self):
        return self.discount_percent > 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)  # для сортировки фото

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} — фото {self.order}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return sum(item.get_subtotal for item in self.items.all())

    @property
    def get_discount(self):
        total = self.get_total
        if total >= Decimal('5000'):
            return total * Decimal('0.10')
        return Decimal('0')

    @property
    def get_final(self):
        return self.get_total - self.get_discount

    def __str__(self):
        return f"Корзина {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def get_subtotal(self):
        return self.product.discounted_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Оформляется'),
        ('delivering', 'Доставляется'),
        ('ready', 'Готов к выдаче'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    delivery = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Заказ #{self.pk} — {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  # фиксируем цену на момент заказа

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

@property
def discounted_price(self):
    if self.discount_percent:
        discount = Decimal(self.discount_percent) / Decimal(100)
        result = self.price * (Decimal(1) - discount)
        return result.quantize(Decimal('0.01'))
    return self.price