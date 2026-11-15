from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.SiteLoginView.as_view(), name='login'),
    path('logout/', views.SiteLogoutView.as_view(), name='logout'),
    path(
        'password-reset/',
        PasswordResetView.as_view(
            template_name='ecommerce/form.html',
            email_template_name='ecommerce/reset_email.txt',
            subject_template_name='ecommerce/reset_subject.txt',
            success_url='/password-reset/done/',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        PasswordResetDoneView.as_view(
            template_name='ecommerce/reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='ecommerce/form.html',
            success_url='/reset/complete/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/complete/',
        PasswordResetCompleteView.as_view(
            template_name='ecommerce/reset_complete.html'
        ),
        name='password_reset_complete',
    ),
    path(
        'product/<int:pk>/',
        views.product_detail,
        name='product_detail',
    ),
    path(
        'product/<int:pk>/review/',
        views.review_create,
        name='review_create',
    ),
    path('stores/', views.my_stores, name='my_stores'),
    path('stores/new/', views.store_create, name='store_create'),
    path('stores/<int:pk>/edit/', views.store_edit, name='store_edit'),
    path('stores/<int:pk>/delete/', views.store_delete, name='store_delete'),
    path(
        'stores/<int:store_id>/products/new/',
        views.product_create,
        name='product_create',
    ),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path(
        'products/<int:pk>/delete/',
        views.product_delete,
        name='product_delete',
    ),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:pk>/', views.add_cart, name='add_cart'),
    path('cart/remove/<int:pk>/', views.remove_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),
]
