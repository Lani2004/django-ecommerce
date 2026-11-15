"""Database models for the marketplace."""

from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Define the Profile class."""
    ROLE_CHOICES = [('buyer', 'Buyer'), ('vendor', 'Vendor')]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        """  str   for the marketplace."""
        return f'{self.user.username} ({self.role})'


class Store(models.Model):
    """Define the Store class."""
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stores',
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    def __str__(self):
        """  str   for the marketplace."""
        return self.name


class Product(models.Model):
    """Define the Product class."""
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='products',
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        """  str   for the marketplace."""
        return self.name


class Order(models.Model):
    """Define the Order class."""
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        """  str   for the marketplace."""
        return f'Order #{self.pk}'


class OrderItem(models.Model):
    """Define the OrderItem class."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class Review(models.Model):
    """Define the Review class."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Define the Meta class."""
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name='rating_between_1_and_5',
            )
        ]
