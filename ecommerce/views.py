"""Views for authentication, stores, products, carts, and orders."""

from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import RegisterForm, StoreForm, ProductForm, ReviewForm
from .models import Profile, Store, Product, Order, OrderItem


class SiteLoginView(LoginView):
    """Define the SiteLoginView class."""
    template_name = 'ecommerce/login.html'
    next_page = reverse_lazy('home')


class SiteLogoutView(LogoutView):
    """Define the SiteLogoutView class."""
    next_page = reverse_lazy('home')


def register(request):
    """Handle register."""
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
            Profile.objects.create(user=user, role=form.cleaned_data['role'])
        login(request, user)
        return redirect('home')
    return render(
        request,
        'ecommerce/form.html',
        {'form': form, 'heading': 'Register'},
    )


def role_required(role):
    """Handle role required."""
    def decorator(view):
        """Wrap a view with a buyer or vendor role check."""
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            """Handle wrapper."""
            if not Profile.objects.filter(
                user=request.user, role=role
            ).exists():
                return HttpResponseForbidden(
                    'This page is for ' + role + ' accounts only.'
                )
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


def home(request):
    """Handle home."""
    return render(
        request,
        'ecommerce/home.html',
        {'products': Product.objects.select_related('store').all()},
    )


def product_detail(request, pk):
    """Handle product detail."""
    product = get_object_or_404(Product, pk=pk)
    already_in_cart = int(request.session.get('cart', {}).get(str(pk), 0))
    available_to_add = max(0, product.stock - already_in_cart)
    return render(
        request,
        'ecommerce/product.html',
        {'product': product, 'available_to_add': available_to_add},
    )


@role_required('vendor')
def my_stores(request):
    """Handle my stores."""
    return render(
        request,
        'ecommerce/stores.html',
        {'stores': Store.objects.filter(vendor=request.user)},
    )


@role_required('vendor')
def store_create(request):
    """Handle store create."""
    form = StoreForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        store = form.save(commit=False)
        store.vendor = request.user
        store.save()
        return redirect('my_stores')
    return render(
        request,
        'ecommerce/form.html',
        {'form': form, 'heading': 'Create store'},
    )


@role_required('vendor')
def store_edit(request, pk):
    """Handle store edit."""
    store = get_object_or_404(Store, pk=pk, vendor=request.user)
    form = StoreForm(request.POST or None, instance=store)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('my_stores')
    return render(
        request,
        'ecommerce/form.html',
        {'form': form, 'heading': 'Edit store'},
    )


@role_required('vendor')
def store_delete(request, pk):
    """Handle store delete."""
    store = get_object_or_404(Store, pk=pk, vendor=request.user)
    if request.method == 'POST':
        try:
            store.delete()
            messages.success(request, 'Store deleted.')
        except Exception:
            messages.error(
                request,
                'Cannot delete a store with products in completed orders.',
            )
        return redirect('my_stores')
    return render(request, 'ecommerce/confirm.html', {'object': store})


@role_required('vendor')
def product_create(request, store_id):
    """Handle product create."""
    store = get_object_or_404(Store, pk=store_id, vendor=request.user)
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.store = store
        product.save()
        return redirect('my_stores')
    return render(
        request,
        'ecommerce/form.html',
        {'form': form, 'heading': 'Add product'},
    )


@role_required('vendor')
def product_edit(request, pk):
    """Handle product edit."""
    product = get_object_or_404(Product, pk=pk, store__vendor=request.user)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('my_stores')
    return render(
        request,
        'ecommerce/form.html',
        {'form': form, 'heading': 'Edit product'},
    )


@role_required('vendor')
def product_delete(request, pk):
    """Handle product delete."""
    product = get_object_or_404(Product, pk=pk, store__vendor=request.user)
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Product deleted.')
        except Exception:
            messages.error(
                request,
                'Cannot delete a product in completed orders.',
            )
        return redirect('my_stores')
    return render(request, 'ecommerce/confirm.html', {'object': product})


def cart_contents(request):
    """Handle cart contents."""
    cart = request.session.get('cart', {})
    products = (
        Product.objects.filter(pk__in=cart.keys())
        .select_related('store')
    )
    lines = [
        {
            'product': p,
            'quantity': int(cart[str(p.pk)]),
            'subtotal': p.price * int(cart[str(p.pk)]),
        }
        for p in products
    ]
    return lines, sum((line['subtotal'] for line in lines), Decimal('0.00'))


@role_required('buyer')
@require_POST
def add_cart(request, pk):
    """Handle add cart."""
    product = get_object_or_404(Product, pk=pk)
    try:
        qty = int(request.POST.get('quantity', '1'))
    except ValueError:
        qty = 0
    if qty < 1 or qty > 1000:
        messages.error(request, 'Enter a quantity between 1 and 1000.')
        return redirect('product_detail', pk=pk)
    cart = request.session.get('cart', {})
    new_qty = int(cart.get(str(pk), 0)) + qty
    if new_qty > product.stock:
        messages.error(request, 'Not enough stock.')
        return redirect('product_detail', pk=pk)
    cart[str(pk)] = new_qty
    request.session['cart'] = cart
    return redirect('cart')


@role_required('buyer')
def cart(request):
    """Handle cart."""
    lines, total = cart_contents(request)
    return render(
        request,
        'ecommerce/cart.html',
        {'lines': lines, 'total': total},
    )


@role_required('buyer')
@require_POST
def remove_cart(request, pk):
    """Handle remove cart."""
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart')


@role_required('buyer')
@require_POST
def checkout(request):
    """Handle checkout."""
    if not request.user.email:
        messages.error(request, 'Please add an email address before checkout.')
        return redirect('cart')
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Cart is empty.')
        return redirect('cart')
    try:
        with transaction.atomic():
            products = list(
                Product.objects.select_for_update().filter(pk__in=cart.keys())
            )
            if len(products) != len(cart):
                raise ValueError('A product is no longer available.')
            lines = []
            total = Decimal('0.00')
            for product in products:
                qty = int(cart[str(product.pk)])
                if qty < 1 or product.stock < qty:
                    raise ValueError('Insufficient stock for ' + product.name)
                subtotal = product.price * qty
                total += subtotal
                lines.append((product, qty, subtotal))
            order = Order.objects.create(buyer=request.user, total=total)
            for product, qty, subtotal in lines:
                Product.objects.filter(pk=product.pk).update(
                    stock=F('stock') - qty
                )
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    unit_price=product.price,
                )
    except (ValueError, TypeError) as exc:
        messages.error(request, str(exc))
        return redirect('cart')
    request.session['cart'] = {}
    invoice = 'Invoice #' + str(order.pk) + '\n' + ''.join(
        f'{p.name} x{q} = AUD {s}\n' for p, q, s in lines
    ) + f'Total: AUD {total}'
    try:
        send_mail(
            'Your MarketPlace invoice #' + str(order.pk),
            invoice,
            None,
            [request.user.email],
            fail_silently=False,
        )
        messages.success(
            request,
            'Order placed. Invoice sent to your email '
            '(or terminal in development).',
        )
    except Exception:
        messages.warning(
            request,
            'Order placed, but invoice email failed. Contact support with '
            'order #' + str(order.pk),
        )
    return render(
        request,
        'ecommerce/invoice.html',
        {'order': order, 'invoice': invoice},
    )


@role_required('buyer')
def review_create(request, pk):
    """Handle review create."""
    product = get_object_or_404(Product, pk=pk)
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.buyer = request.user
        review.verified = (
            OrderItem.objects.filter(
                product=product,
                order__buyer=request.user,
            ).exists()
        )
        review.save()
        return redirect('product_detail', pk=pk)
    return render(
        request,
        'ecommerce/form.html',
        {'form': form, 'heading': 'Review ' + product.name},
    )
