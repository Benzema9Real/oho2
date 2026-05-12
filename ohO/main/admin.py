from django.contrib import admin
from .models import Product, ProductImage, Color, Category, Cart, CartItem, Order, OrderItem, Favorite


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_subtotal',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price_at_purchase',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'category', 'price', 'discount_percent', 'is_new', 'stock')
    list_filter = ('category', 'is_new', 'colors')
    search_fields = ('name', 'description')
    list_editable = ('price', 'discount_percent', 'is_new', 'stock')
    filter_horizontal = ('colors',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('user', 'get_total', 'created_at')
    readonly_fields = ('get_total', 'get_discount', 'get_final')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'user', 'status', 'delivery', 'total_price', 'created_at')
    list_filter = ('status', 'delivery')
    list_editable = ('status',)
    search_fields = ('user__username',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')