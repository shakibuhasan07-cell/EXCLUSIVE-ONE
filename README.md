# EXCLUSIVE ONE V3.1.0

This build upgrades the original V1 Flask store while keeping its core shopping flow and adding the requested V3 features.

## Included
- V1 product/shop/cart/checkout/account/order flow retained
- V1 compatibility routes for `/add/<id>` and `/remove/<id>` (POST + CSRF)
- 14 seeded products including Men, Women, Children, Shoes and Gadgets
- Size selection, Buy Now, cart quantity controls, wishlist and reviews
- Email OR Bangladesh mobile account creation/login/recovery
- CAPTCHA and login throttling
- Profile picture upload with circular avatar UI
- bKash, Nagad, Rocket, Bank Card and Cash on Delivery payment choices
- Admin product creation, stock, sizes and order status
- Contact: +8801609228262 / exclusiveone1@gmail.com
- Instagram: exclusive_one1 / Facebook: Exclusive ONE
- Responsive animated storefront and mobile navigation
- CSRF protection, password hashing, secure session settings, security headers and safe image uploads
- Automatic V1 database import when the old `users.db` is placed beside `app.py`

## Run
```text
pip install -r requirements.txt
py app.py
```
Open `http://127.0.0.1:5000`.

## Admin
Default local admin: `admin@exclusive-one.local` / `ChangeMe123!`. Change it through environment variables before production.

## V1 data migration
Do not delete the old V1 folder. If you want to import the old `users.db`, copy that file into the V3.1.0 project folder beside `app.py`. On startup, existing V3 records are not overwritten.

## Real payments/email
The payment choices are UI/order-recording support. Real bKash/Nagad/Rocket/card gateway APIs must be connected separately; no raw card number is stored. SMTP settings can be configured through environment variables for real reset/contact email delivery.
