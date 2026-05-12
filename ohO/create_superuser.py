import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oho_kg.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'skinsfarmemir.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Суперпользователь {username} создан')
else:
    print(f'Суперпользователь {username} уже существует')