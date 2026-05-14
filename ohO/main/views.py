from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .models import Product, Category, Color, Cart, CartItem, Order, OrderItem, Favorite


# ───────────────────────────── ГЛАВНАЯ ─────────────────────────────

def index(request):
    new_products = Product.objects.filter(is_new=True).prefetch_related('images', 'colors')[:6]
    favorite_ids = []
    cart_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
        try:
            cart_ids = list(request.user.cart.items.values_list('product_id', flat=True))
        except:
            cart_ids = []
    return render(request, 'index.html', {
        'new_products': new_products,
        'favorite_ids': favorite_ids,
        'cart_ids': cart_ids,
    })


# ───────────────────────────── КАТАЛОГ ─────────────────────────────

def catalog(request):
    products = Product.objects.prefetch_related('images', 'colors').select_related('category')

    # фильтр по категории (вкладки)
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # фильтр по цвету
    color_ids = request.GET.getlist('color')
    if color_ids:
        products = products.filter(colors__id__in=color_ids).distinct()

    # фильтр по цене
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # кнопки «новинки» и «со скидкой»
    if request.GET.get('is_new'):
        products = products.filter(is_new=True)
    if request.GET.get('on_sale'):
        products = products.filter(discount_percent__gt=0)

    # сортировка
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    # пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)

    categories = Category.objects.all()
    colors = Color.objects.all()

    favorite_ids = []
    cart_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
        try:
            cart_ids = list(request.user.cart.items.values_list('product_id', flat=True))
        except:
            cart_ids = []

    return render(request, 'catalog.html', {
        'products': products_page,
        'categories': categories,
        'colors': colors,
        'favorite_ids': favorite_ids,
        'current_category': category_slug,
        'selected_colors': [int(c) for c in color_ids] if color_ids else [],
        'sort': sort,
        'cart_ids': cart_ids,
    })

# ───────────────────────────── КАРТОЧКА ТОВАРА ─────────────────────────────

def product_detail(request, pk):
    product = get_object_or_404(Product.objects.prefetch_related('images', 'colors'), pk=pk)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    return render(request, 'product_detail.html', {
        'product': product,
        'is_favorite': is_favorite,
    })


# ───────────────────────────── КОРЗИНА ─────────────────────────────

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').prefetch_related('product__images')
    return render(request, 'cart.html', {'cart': cart, 'items': items})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')


@login_required
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty > 0:
        item.quantity = qty
        item.save()
    else:
        item.delete()
    return redirect('cart')


# ───────────────────────────── ОФОРМЛЕНИЕ ЗАКАЗА ─────────────────────────────
@login_required
def checkout_delivery(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        return redirect('cart')

    if request.method == 'POST':
        delivery = request.POST.get('delivery') == 'true'
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        request.session['checkout_delivery'] = delivery
        request.session['checkout_address'] = address
        request.session['checkout_phone'] = phone
        return redirect('checkout_payment')

    return render(request, 'checkout_delivery.html', {'cart': cart})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.status == 'processing':
        order.status = 'cancelled'
        order.save()
    return redirect('my_orders')

@login_required
def checkout_payment(request):
    """Шаг 2 — оплата (заглушка)"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # создаём заказ
        delivery = request.session.get('checkout_delivery', False)
        address = request.session.get('checkout_address', '')
        order = Order.objects.create(
            user=request.user,
            delivery=delivery,
            address=address if delivery else '',
            phone=request.session.get('checkout_phone', ''),
            total_price=cart.get_final,
            status='processing',
        )
        for item in cart.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.discounted_price,
            )
        cart.items.all().delete()
        request.session.pop('checkout_delivery', None)
        request.session.pop('checkout_address', None)
        return redirect('checkout_status', order_id=order.pk)

    return render(request, 'checkout_payment.html', {'cart': cart})


@login_required
def checkout_status(request, order_id):
    """Шаг 3 — статус заказа"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'checkout_status.html', {'order': order})


# ───────────────────────────── МОИ ЗАКАЗЫ ─────────────────────────────

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


# ───────────────────────────── ИЗБРАННОЕ ─────────────────────────────

@login_required
def favorites(request):
    favs = Favorite.objects.filter(user=request.user).select_related('product').prefetch_related('product__images')
    return render(request, 'favorites.html', {'favs': favs})


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))


# ───────────────────────────── РЕГИСТРАЦИЯ / ЛОГИН / ВЫХОД ─────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        Cart.objects.create(user=user)  # сразу создаём корзину
        login(request, user)
        return redirect('index')
    return render(request, 'register.html', {'form': form})


@login_required
def ajax_cart_toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = CartItem.objects.filter(cart=cart, product=product).first()
    if item:
        item.delete()
        in_cart = False
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        in_cart = True
    cart_count = cart.items.count()
    return JsonResponse({'in_cart': in_cart, 'cart_count': cart_count})


@login_required
def ajax_favorite_toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        is_fav = False
    else:
        is_fav = True
    return JsonResponse({'is_fav': is_fav})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = AuthenticationForm(data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'index'))
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.prefetch_related('images', 'colors'), pk=pk)
    is_favorite = False
    is_in_cart = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
        try:
            is_in_cart = request.user.cart.items.filter(product=product).exists()
        except:
            is_in_cart = False
    return render(request, 'product_detail.html', {
        'product': product,
        'is_favorite': is_favorite,
        'is_in_cart': is_in_cart,
    })