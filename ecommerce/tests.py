"""Tests for marketplace permissions and shopping behaviour."""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile, Store, Product


class MarketplaceTests(TestCase):
    """Define the MarketplaceTests class."""
    def setUp(self):
        """Setup for the marketplace."""
        self.vendor = User.objects.create_user(
            "vendor", password="StrongTestPass123!"
        )
        self.buyer = User.objects.create_user(
            "buyer",
            email="buyer@example.com",
            password="StrongTestPass123!",
        )
        Profile.objects.create(user=self.vendor, role="vendor")
        Profile.objects.create(user=self.buyer, role="buyer")
        self.store = Store.objects.create(vendor=self.vendor, name="Demo")
        self.product = Product.objects.create(
            store=self.store,
            name="Notebook",
            price="12.50",
            stock=5,
        )

    def test_buyer_cannot_edit_vendor_product(self):
        """Test buyer cannot edit vendor product for the marketplace."""
        self.client.force_login(self.buyer)
        response = self.client.get(
            reverse("product_edit", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_checkout_and_verified_review(self):
        """Test checkout and verified review for the marketplace."""
        self.client.force_login(self.buyer)
        self.client.post(
            reverse("add_cart", args=[self.product.pk]),
            {"quantity": "2"},
        )
        response = self.client.post(reverse("checkout"))
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.client.post(
            reverse("review_create", args=[self.product.pk]),
            {"rating": 5, "comment": "Great"},
        )
        self.assertTrue(self.product.reviews.first().verified)

    def test_vendor_cannot_see_buyer_cart_controls(self):
        """Test vendor cannot see buyer cart controls for the marketplace."""
        self.client.force_login(self.vendor)
        response = self.client.get(
            reverse("product_detail", args=[self.product.pk])
        )
        self.assertNotContains(response, "Add to cart")

    def test_buyer_navigation_and_quantity_limit(self):
        """Test buyer navigation and quantity limit for the marketplace."""
        self.client.force_login(self.buyer)
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "My stores")
        self.assertContains(response, "Cart")
        response = self.client.get(
            reverse("product_detail", args=[self.product.pk])
        )
        self.assertContains(response, 'max="5"')
        self.client.post(
            reverse("add_cart", args=[self.product.pk]),
            {"quantity": "2"},
        )
        self.assertContains(
            self.client.get(reverse("cart")), "Continue Shopping"
        )

    def test_rating_input_is_limited(self):
        """Test rating input is limited for the marketplace."""
        self.client.force_login(self.buyer)
        response = self.client.get(
            reverse("review_create", args=[self.product.pk])
        )
        self.assertContains(response, 'max="5"')
        self.assertContains(response, 'min="1"')

    def test_quantity_field_accounts_for_items_already_in_cart(self):
        """Limit the displayed quantity to the remaining available stock."""
        self.client.force_login(self.buyer)
        self.client.post(
            reverse('add_cart', args=[self.product.pk]),
            {'quantity': '3'},
        )
        response = self.client.get(
            reverse('product_detail', args=[self.product.pk])
        )
        self.assertContains(response, 'max="2"')
        response = self.client.post(
            reverse('add_cart', args=[self.product.pk]),
            {'quantity': '3'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['cart'][str(self.product.pk)], 3)

    def test_vendor_cannot_access_cart(self):
        """Block vendors from buyer-only cart pages."""
        self.client.force_login(self.vendor)
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 403)

    def test_invalid_rating_is_not_saved(self):
        """Reject a review rating outside the one-to-five range."""
        self.client.force_login(self.buyer)
        response = self.client.post(
            reverse('review_create', args=[self.product.pk]),
            {'rating': 6, 'comment': 'Invalid'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.product.reviews.exists())
