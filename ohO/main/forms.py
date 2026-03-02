from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

from .models import Product, ProductImage
from django.forms import modelformset_factory
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'


ProductImageFormSet = modelformset_factory(
    ProductImage,
    form=ProductImageForm,
    extra=3,
    max_num=10,
    validate_max=True
)


class RegisterForm(UserCreationForm):
    name = forms.CharField(label='Имя', max_length=100)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


User = get_user_model()

class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Неверный email или пароль")

        user = authenticate(username=user.username, password=password)
        if user is None:
            raise ValidationError("Неверный email или пароль")
        self.user = user
        return self.cleaned_data

    def get_user(self):
        return self.user