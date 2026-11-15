# MarketPlace — Planning

## Requirements
- Vendors register, log in, create/edit/delete their own stores and products.
- Buyers register, log in, browse all products, add/remove cart items, check out, receive invoice emails and review products.
- Reviews are verified if the buyer has an OrderItem for that product; otherwise unverified.
- Password reset uses Django's built-in time-limited, signed reset tokens.
- MariaDB relational database for the running application, with Django migrations. SQLite is used only for isolated automated tests.

## UI layout
Top navigation: products, login/register or stores/cart/logout. Product listing links to detail pages. Vendor dashboard contains store and product actions. Buyer cart shows subtotals and checkout.

## Access/security
Django authentication, CSRF middleware, password validators and role checks. Vendors only modify their own records; buyers only access cart, checkout and reviews. Login required for protected views. No payment processing is implemented.

## Failure handling
Invalid forms show validation errors; missing records return 404; unauthorised roles receive 403; insufficient stock blocks checkout; atomic database transactions avoid partial orders; invoice email failures are reported without undoing an already committed order. For production, use a real SMTP service, HTTPS, a secret environment key and an order/email retry queue.

## Sequence
Buyer -> login -> browse -> add to session cart -> checkout -> verify stock -> atomic order and inventory update -> clear cart -> invoice email.

## User journeys
### Buyer
1. Register as a buyer and log in.
2. Browse products and open a product detail page.
3. Choose a quantity no greater than remaining stock and add it to the session cart.
4. Continue shopping or open the cart to remove an item.
5. Check out: the system checks inventory, saves the order, reduces stock and creates an invoice.
6. Leave a rating between 1 and 5. The review is verified only if this buyer previously purchased the product.

### Vendor
1. Register as a vendor and log in.
2. Open My stores to create or edit a store.
3. Add, update or delete products belonging to that vendor's stores.
4. Do not show buyer-only Cart or Checkout links; the server also checks roles for protected views.

## UI and accessibility details
- The navigation displays My stores for vendors and Cart for buyers, never both.
- Product pages show name, store, description, price and available stock.
- Quantity input has a minimum of one and a maximum based on stock remaining after items already in the cart.
- The cart displays each item's subtotal, a checkout action and a Continue Shopping link.
- Review rating uses a number input with limits of one to five.
- Forms use visible labels, validation messages and a consistent layout.

## Database and installation plan
- MariaDB is the application database; connection details come from environment variables.
- First create the database and dedicated user, then install dependencies, run migrations and create a Django superuser.
- Keep passwords and secret keys out of source control using `.env` and `.gitignore`.
- Include cloning and setup steps in README.md so a new developer can reproduce the project.

## Testing and failure scenarios
- Check that a buyer cannot edit a vendor's products and a vendor cannot use buyer-only cart functions.
- Check that stock cannot be exceeded through either the input field or a direct POST request.
- Reject ratings outside one to five, including direct POST requests.
- If stock changes before checkout, display an error and do not create a partial order.
- If invoice delivery fails after a successful order, keep the order and show a warning.
- Test password reset using the development email backend and an expiring link.
