# Django eCommerce Application – Practical Task 1

## About the project
I built this Django website for my HyperionDev practical task. Buyers can browse products, add items to their cart, check out and leave reviews. Vendors can manage their own stores and products. Buyer and vendor pages have different access permissions.

## Features
- Register as a buyer or vendor, log in and log out.
- Vendors can create, edit and remove their stores and products.
- Buyers can browse products, add quantities up to the available stock, continue shopping, and check out.
- Checkout reduces stock, creates an order and produces an invoice email (shown in the terminal in development).
- Buyers can leave ratings from 1 to 5. Reviews are marked verified when the buyer purchased that product.
- Password reset uses Django's expiring reset links.

## Technologies
Python, Django, HTML, CSS and MariaDB. SQLite is available for local automated tests only.

## Download and open the project
1. Clone your own GitHub repository (replace the example with your actual repository URL):
   ```bash
   git clone https://github.com/Lani2004/django-ecommerce.git
   cd django-ecommerce
   ```
   If you already downloaded the ZIP, open the extracted `marketplace_project` folder instead.
2. Create and activate the virtual environment **inside** the project folder:
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```
3. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```
   On macOS, `mysqlclient` may require MariaDB Connector/C or MySQL client development libraries installed through Homebrew.

## Set up the MariaDB database
1. Install and start MariaDB on your computer. Log in to its SQL console as an administrator.
2. Create the database and a user (replace the example password with your own):
   ```sql
   CREATE DATABASE marketplace_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'marketplace_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
   GRANT ALL PRIVILEGES ON marketplace_db.* TO 'marketplace_user'@'localhost';
   ```
   If you use `DB_HOST=127.0.0.1`, also create/grant the corresponding `marketplace_user`@`127.0.0.1` account if your MariaDB setup requires it, or use `DB_HOST=localhost`.
3. Copy `.env.example` to `.env`. Set your own `DB_PASSWORD` and `DJANGO_SECRET_KEY`. **Do not upload `.env` to GitHub.** Django reads environment variables from your shell, so load them before running commands:
   ```bash
   set -a
   source .env
   set +a
   ```
4. Create migration files if models have changed, then apply them to MariaDB:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```
5. Create a new administrator account **after migrating**:
   ```bash
   python3 manage.py createsuperuser
   ```
   Enter your username, email and password when prompted. These are your own new credentials, not the MariaDB database login.
6. Check the project and run the server:
   ```bash
   python3 manage.py check
   python3 manage.py runserver
   ```
7. Open http://127.0.0.1:8000/ for the shop, or http://127.0.0.1:8000/admin/ for Django administration.

## Running automated tests
To run the existing tests using a separate temporary SQLite test database:
```bash
DB_ENGINE=sqlite python3 manage.py test
```

## Planning
My detailed requirements are in `Planning/requirements.md`. They describe buyer and vendor journeys, the interface, access restrictions, database setup and error handling.

## What I learned
I practised using Django models, views, forms, templates, login permissions, databases, sessions and testing. I also learned why the database needs migrations and why buyers and vendors should not have the same access.

## Notes
This is a learning project, not a live payment service. Email is printed in the terminal by default. For a real deployment, use secure production settings, an email service and a payment provider.

## Publish the project to GitHub
Create an empty repository on your GitHub account, then from the project folder run:
```bash
git init
git add .
git commit -m "Complete Django eCommerce practical task 1"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
Replace the repository URL with your own. Do not commit `.env`, `myenv/`, or your local database.

## Manual checks before submission
1. Register a buyer and a vendor account separately.
2. Confirm the buyer sees Cart but not My stores; the vendor sees My stores but not Cart.
3. Confirm vendors cannot open buyer-only cart URLs and buyers cannot edit vendor products.
4. Add a product to the cart, return to the product page and confirm the quantity maximum accounts for items already in the cart.
5. Confirm Continue Shopping returns to the product list.
6. Confirm reviews only accept 1–5, and checkout reduces stock and produces an invoice.
7. Test password reset and inspect the email link printed to the development terminal.
