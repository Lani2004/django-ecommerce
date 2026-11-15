from django.contrib import admin
from .models import Profile, Store, Product, Order, OrderItem, Review
for model in (Profile, Store, Product, Order, OrderItem, Review):
    admin.site.register(model)
