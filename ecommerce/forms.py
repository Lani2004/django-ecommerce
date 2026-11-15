"""Forms for registration, stores, products, and reviews."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Store, Product, Review


class RegisterForm(UserCreationForm):
    """Define the RegisterForm class."""
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('buyer', 'Buyer'), ('vendor', 'Vendor')]
    )

    class Meta(UserCreationForm.Meta):
        """Define the Meta class."""
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def clean_email(self):
        """Clean email for the marketplace."""
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email

    def save(self, commit=True):
        """Save for the marketplace."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class StoreForm(forms.ModelForm):
    """Define the StoreForm class."""
    class Meta:
        """Define the Meta class."""
        model = Store
        fields = ('name', 'description')


class ProductForm(forms.ModelForm):
    """Define the ProductForm class."""
    class Meta:
        """Define the Meta class."""
        model = Product
        fields = ('name', 'description', 'price', 'stock')


class ReviewForm(forms.ModelForm):
    """Define the ReviewForm class."""
    class Meta:
        """Define the Meta class."""
        model = Review
        fields = ('rating', 'comment')

    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 1}),
    )

    def clean_rating(self):
        """Clean rating for the marketplace."""
        n = self.cleaned_data['rating']
        if n < 1 or n > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return n
