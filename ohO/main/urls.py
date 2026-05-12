from django.urls import path
from . import views

urlpatterns = [
    # главная
    path('', views.index, name='index'),

    # каталог и товар
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),

    # оформление заказа
    path('checkout/', views.checkout_delivery, name='checkout_delivery'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/status/<int:order_id>/', views.checkout_status, name='checkout_status'),
    path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    # заказы и избранное
    path('orders/', views.my_orders, name='my_orders'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),

    # авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('ajax/cart/<int:product_id>/', views.ajax_cart_toggle, name='ajax_cart_toggle'),
    path('ajax/favorite/<int:product_id>/', views.ajax_favorite_toggle, name='ajax_favorite_toggle'),
]
