from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from .models import Product


def main_view(request):
    new_products = Product.objects.filter(is_new=True)
    return render(request, 'main.html', {'products': new_products})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main')  # перенаправление на главную
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})
