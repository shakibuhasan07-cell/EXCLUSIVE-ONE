from flask import Flask, request, redirect, url_for, session, render_template_string
from flask import Response

app = Flask(__name__)
app.secret_key = "exclusive-one-secret-key"


@app.route("/sw.js")
def service_worker():
    response = app.send_static_file("sw.js")
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Service-Worker-Allowed"] = "/"
    return response

# =========================================================
# EXCLUSIVE ONE - PRODUCT DATA
# =========================================================

PRODUCTS = [
    {
        "id": 1,
        "name": "Premium Oversized T-Shirt",
        "category": "Men",
        "price": 899,
        "old_price": 1199,
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800",
        "description": "Premium cotton oversized t-shirt with a clean modern fit."
    },
    {
        "id": 2,
        "name": "Classic Black Shirt",
        "category": "Men",
        "price": 1299,
        "old_price": 1599,
        "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800",
        "description": "Minimal classic shirt designed for smart casual looks."
    },
    {
        "id": 3,
        "name": "Elegant Women's Dress",
        "category": "Women",
        "price": 1899,
        "old_price": 2299,
        "image": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=800",
        "description": "Elegant premium dress with a sophisticated aesthetic."
    },
    {
        "id": 4,
        "name": "Premium Hand Bag",
        "category": "Accessories",
        "price": 1599,
        "old_price": 1999,
        "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800",
        "description": "Stylish premium handbag suitable for everyday use."
    },
    {
        "id": 5,
        "name": "Luxury Sunglasses",
        "category": "Accessories",
        "price": 999,
        "old_price": 1299,
        "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800",
        "description": "Modern sunglasses with a premium luxury appearance."
    },
    {
        "id": 6,
        "name": "Minimalist Watch",
        "category": "Lifestyle",
        "price": 2199,
        "old_price": 2799,
        "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800",
        "description": "Minimalist watch designed for modern everyday style."
    },
    {
        "id": 7,
        "name": "Premium Hoodie",
        "category": "Men",
        "price": 1699,
        "old_price": 2099,
        "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800",
        "description": "Comfortable premium hoodie with a modern streetwear fit."
    },
    {
        "id": 8,
        "name": "Women's Casual Top",
        "category": "Women",
        "price": 1099,
        "old_price": 1399,
        "image": "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?w=800",
        "description": "Simple and elegant casual top for everyday fashion."
    },
]

# =========================================================
# HTML TEMPLATE
# =========================================================

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#0F1626">

<title>{{ title }} | EXCLUSIVE ONE</title>

<style>

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    background: #14171C;
    color: #EDEBE6;
}

a {
    color: inherit;
    text-decoration: none;
}

.container {
    width: 92%;
    max-width: 1250px;
    margin: auto;
}

/* ================= HEADER ================= */

header {
    background: #0F1626;
    border-bottom: 1px solid #2E343E;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar {
    min-height: 75px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 25px;
}

.logo {
    font-size: 25px;
    font-weight: 800;
    letter-spacing: 3px;
    color: #EDEBE6;
}

.logo span {
    color: #C9B79C;
}

.nav-links {
    display: flex;
    gap: 22px;
    align-items: center;
}

.nav-links a {
    color: #C4C9D1;
    font-size: 14px;
    transition: .3s;
}

.nav-links a:hover {
    color: #C9B79C;
}

.search-box {
    display: flex;
    gap: 5px;
}

.search-box input {
    width: 180px;
    padding: 10px 12px;
    background: #1B1F26;
    color: white;
    border: 1px solid #2E343E;
    border-radius: 8px;
}

.search-box button {
    background: #C9B79C;
    border: none;
    padding: 0 13px;
    border-radius: 8px;
    cursor: pointer;
}

/* ================= HERO ================= */

.hero {
    min-height: 500px;
    display: flex;
    align-items: center;
    background:
        linear-gradient(
            90deg,
            rgba(15,22,38,.95),
            rgba(20,23,28,.55)
        ),
        url("https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1600")
        center/cover;
}

.hero-content {
    max-width: 650px;
}

.hero h1 {
    font-size: clamp(42px, 7vw, 75px);
    line-height: 1;
    margin-bottom: 20px;
}

.hero h1 span {
    color: #C9B79C;
}

.hero p {
    color: #C4C9D1;
    line-height: 1.7;
    margin-bottom: 30px;
}

.btn {
    display: inline-block;
    padding: 13px 23px;
    border-radius: 8px;
    border: 1px solid #C9B79C;
    background: #C9B79C;
    color: #14171C;
    font-weight: bold;
    cursor: pointer;
}

.btn-dark {
    background: transparent;
    color: #EDEBE6;
}

/* ================= SECTION ================= */

.section {
    padding: 65px 0;
}

.section-title {
    margin-bottom: 30px;
}

.section-title h2 {
    font-size: 32px;
}

.section-title p {
    color: #9AA1AC;
    margin-top: 8px;
}

/* ================= CATEGORY ================= */

.categories {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}

.category {
    background: #1B1F26;
    padding: 35px 20px;
    text-align: center;
    border: 1px solid #2E343E;
    border-radius: 12px;
    transition: .3s;
}

.category:hover {
    transform: translateY(-5px);
    border-color: #C9B79C;
}

.category h3 {
    margin-bottom: 8px;
}

.category p {
    color: #9AA1AC;
}

/* ================= PRODUCTS ================= */

.products {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
}

.product {
    background: #1B1F26;
    border: 1px solid #2E343E;
    border-radius: 12px;
    overflow: hidden;
    transition: .3s;
}

.product:hover {
    transform: translateY(-5px);
    border-color: #C9B79C;
}

.product-img {
    width: 100%;
    height: 270px;
    object-fit: cover;
}

.product-info {
    padding: 17px;
}

.product-category {
    color: #9AA1AC;
    font-size: 12px;
}

.product-name {
    font-size: 17px;
    margin: 7px 0;
}

.price {
    color: #C9B79C;
    font-size: 19px;
    font-weight: bold;
}

.old-price {
    color: #777;
    text-decoration: line-through;
    margin-left: 7px;
    font-size: 13px;
}

.product-actions {
    display: flex;
    gap: 8px;
    margin-top: 14px;
}

.product-actions a {
    flex: 1;
    text-align: center;
    padding: 9px;
    border-radius: 7px;
    background: #232831;
    font-size: 13px;
}

.product-actions a:hover {
    background: #C9B79C;
    color: #14171C;
}

/* ================= PRODUCT DETAILS ================= */

.product-detail {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 45px;
    padding: 70px 0;
}

.product-detail img {
    width: 100%;
    max-height: 600px;
    object-fit: cover;
    border-radius: 15px;
}

.detail-info h1 {
    font-size: 42px;
    margin: 15px 0;
}

.detail-info p {
    color: #9AA1AC;
    line-height: 1.8;
    margin: 20px 0;
}

/* ================= CART ================= */

.cart-item {
    display: flex;
    align-items: center;
    gap: 20px;
    background: #1B1F26;
    padding: 15px;
    margin-bottom: 12px;
    border: 1px solid #2E343E;
    border-radius: 10px;
}

.cart-item img {
    width: 90px;
    height: 90px;
    object-fit: cover;
    border-radius: 8px;
}

.cart-total {
    text-align: right;
    padding: 25px 0;
    font-size: 25px;
}

/* ================= FORM ================= */

.form-box {
    max-width: 600px;
    margin: 50px auto;
    background: #1B1F26;
    border: 1px solid #2E343E;
    padding: 30px;
    border-radius: 12px;
}

.form-box input,
.form-box textarea,
.form-box select {
    width: 100%;
    padding: 13px;
    margin: 8px 0 17px;
    background: #14171C;
    color: white;
    border: 1px solid #2E343E;
    border-radius: 7px;
}

/* ================= FOOTER ================= */

footer {
    margin-top: 70px;
    background: #0F1626;
    border-top: 1px solid #2E343E;
    padding: 45px 0 25px;
}

.footer-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 35px;
}

footer h3 {
    margin-bottom: 15px;
}

footer p,
footer a {
    color: #9AA1AC;
    line-height: 2;
    font-size: 14px;
}

.footer-bottom {
    margin-top: 35px;
    padding-top: 20px;
    border-top: 1px solid #2E343E;
    display: flex;
    justify-content: space-between;
    color: #777;
    font-size: 13px;
}

.powered {
    color: #C9B79C;
    font-weight: bold;
}

/* ================= RESPONSIVE ================= */

@media(max-width: 900px) {

    .nav-links {
        display: none;
    }

    .categories,
    .products {
        grid-template-columns: repeat(2, 1fr);
    }

    .product-detail {
        grid-template-columns: 1fr;
    }

    .footer-grid {
        grid-template-columns: 1fr 1fr;
    }
}

@media(max-width: 600px) {

    .search-box {
        display: none;
    }

    .categories,
    .products {
        grid-template-columns: 1fr;
    }

    .hero {
        min-height: 450px;
    }

    .footer-grid {
        grid-template-columns: 1fr;
    }

    .footer-bottom {
        flex-direction: column;
        gap: 10px;
    }
}

</style>
</head>

<body>

<header>

<div class="container navbar">

<a href="{{ url_for('home') }}" class="logo">
EXCLUSIVE <span>ONE</span>
</a>

<nav class="nav-links">
<a href="{{ url_for('home') }}">Home</a>
<a href="{{ url_for('shop') }}">Shop</a>
<a href="{{ url_for('shop', category='Men') }}">Men</a>
<a href="{{ url_for('shop', category='Women') }}">Women</a>
<a href="{{ url_for('shop', category='Accessories') }}">Accessories</a>
<a href="{{ url_for('cart') }}">Cart 🛒</a>
</nav>

<form class="search-box" action="{{ url_for('shop') }}">
<input name="q" placeholder="Search products...">
<button type="submit">⌕</button>
</form>

</div>

</header>

{% block_content %}

<footer>

<div class="container">

<div class="footer-grid">

<div>
<h3>EXCLUSIVE ONE</h3>
<p>
Premium fashion, accessories and lifestyle products
for people who love modern style.
</p>
</div>

<div>
<h3>Shop</h3>
<p><a href="{{ url_for('shop') }}">All Products</a></p>
<p><a href="{{ url_for('shop', category='Men') }}">Men</a></p>
<p><a href="{{ url_for('shop', category='Women') }}">Women</a></p>
</div>

<div>
<h3>Help</h3>
<p><a href="#">Contact</a></p>
<p><a href="#">FAQ</a></p>
<p><a href="#">Shipping</a></p>
<p><a href="#">Returns</a></p>
</div>

<div>
<h3>Company</h3>
<p><a href="#">About Us</a></p>
<p><a href="#">Privacy</a></p>
<p><a href="#">Terms</a></p>
</div>

</div>

<div class="footer-bottom">

<div>
© 2026 EXCLUSIVE ONE. All Rights Reserved.
</div>

<div>
Powered by <span class="powered">SHAKIBUL HASAN</span>
</div>

</div>

</div>

</footer>

</body>
</html>
"""


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    featured = PRODUCTS[:4]

    content = """

<section class="hero">

<div class="container hero-content">

<h1>
Define Your
<span>Style.</span>
</h1>

<p>
Discover premium fashion, accessories and lifestyle
products carefully selected for the modern generation.
</p>

<a class="btn" href="/shop">
SHOP NOW
</a>

<a class="btn btn-dark" href="/shop">
EXPLORE
</a>

</div>

</section>


<section class="section">

<div class="container">

<div class="section-title">
<h2>Shop by Category</h2>
<p>Explore our collections.</p>
</div>

<div class="categories">

<a class="category" href="/shop?category=Men">
<h3>Men</h3>
<p>Modern men's fashion</p>
</a>

<a class="category" href="/shop?category=Women">
<h3>Women</h3>
<p>Elegant women's fashion</p>
</a>

<a class="category" href="/shop?category=Accessories">
<h3>Accessories</h3>
<p>Complete your look</p>
</a>

<a class="category" href="/shop?category=Lifestyle">
<h3>Lifestyle</h3>
<p>Everyday premium living</p>
</a>

</div>

</div>

</section>


<section class="section">

<div class="container">

<div class="section-title">
<h2>Featured Collection</h2>
<p>Our most popular products.</p>
</div>

<div class="products">

{% for product in products %}

<div class="product">

<img
class="product-img"
src="{{ product.image }}"
alt="{{ product.name }}"
>

<div class="product-info">

<div class="product-category">
{{ product.category }}
</div>

<div class="product-name">
{{ product.name }}
</div>

<div>

<span class="price">
৳{{ product.price }}
</span>

<span class="old-price">
৳{{ product.old_price }}
</span>

</div>

<div class="product-actions">

<a href="/product/{{ product.id }}">
View
</a>

<a href="/add/{{ product.id }}">
Add Cart
</a>

</div>

</div>

</div>

{% endfor %}

</div>

</div>

</section>
"""

    return render_template_string(
        BASE_HTML.replace("{% block_content %}", content),
        title="Home",
        products=featured
    )


# =========================================================
# SHOP
# =========================================================

@app.route("/shop")
def shop():

    query = request.args.get("q", "").lower()
    category = request.args.get("category", "")

    filtered = PRODUCTS

    if query:
        filtered = [
            p for p in filtered
            if query in p["name"].lower()
            or query in p["category"].lower()
        ]

    if category:
        filtered = [
            p for p in filtered
            if p["category"].lower() == category.lower()
        ]

    content = """

<section class="section">

<div class="container">

<div class="section-title">

<h2>Shop</h2>

<p>
{% if query %}
Search results for "{{ query }}"
{% elif category %}
{{ category }} Collection
{% else %}
All Products
{% endif %}
</p>

</div>

<div class="products">

{% for product in products %}

<div class="product">

<img class="product-img"
src="{{ product.image }}"
alt="{{ product.name }}">

<div class="product-info">

<div class="product-category">
{{ product.category }}
</div>

<div class="product-name">
{{ product.name }}
</div>

<div>

<span class="price">
৳{{ product.price }}
</span>

<span class="old-price">
৳{{ product.old_price }}
</span>

</div>

<div class="product-actions">

<a href="/product/{{ product.id }}">
View
</a>

<a href="/add/{{ product.id }}">
Add Cart
</a>

</div>

</div>

</div>

{% else %}

<p>No products found.</p>

{% endfor %}

</div>

</div>

</section>
"""

    return render_template_string(
        BASE_HTML.replace("{% block_content %}", content),
        title="Shop",
        products=filtered,
        query=query,
        category=category
    )


# =========================================================
# PRODUCT DETAILS
# =========================================================

@app.route("/product/<int:product_id>")
def product(product_id):

    product = next(
        (p for p in PRODUCTS if p["id"] == product_id),
        None
    )

    if not product:
        return "Product not found", 404

    content = """

<section class="container">

<div class="product-detail">

<div>
<img src="{{ product.image }}" alt="{{ product.name }}">
</div>

<div class="detail-info">

<div class="product-category">
{{ product.category }}
</div>

<h1>
{{ product.name }}
</h1>

<div>

<span class="price">
৳{{ product.price }}
</span>

<span class="old-price">
৳{{ product.old_price }}
</span>

</div>

<p>
{{ product.description }}
</p>

<a class="btn" href="/add/{{ product.id }}">
ADD TO CART
</a>

</div>

</div>

</section>
"""

    return render_template_string(
        BASE_HTML.replace("{% block_content %}", content),
        title=product["name"],
        product=product
    )


# =========================================================
# ADD TO CART
# =========================================================

@app.route("/add/<int:product_id>")
def add_to_cart(product_id):

    cart = session.get("cart", {})
    product_id = str(product_id)
    cart[product_id] = cart.get(product_id, 0) + 1
    session["cart"] = cart

    return redirect(url_for("cart"))


# =========================================================
# REMOVE FROM CART
# =========================================================

@app.route("/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    session["cart"] = cart

    return redirect(url_for("cart"))


# =========================================================
# CART
# =========================================================

@app.route("/cart")
def cart():

    cart_data = []
    total = 0

    cart = session.get("cart", {})

    for product_id, quantity in cart.items():

        product = next(
            (p for p in PRODUCTS if p["id"] == int(product_id)),
            None
        )

        if product:

            subtotal = product["price"] * quantity
            total += subtotal

            cart_data.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

    content = """

<section class="section">

<div class="container">

<div class="section-title">
<h2>Your Cart</h2>
<p>{{ cart_data|length }} product(s)</p>
</div>

{% for item in cart_data %}

<div class="cart-item">

<img
src="{{ item.product.image }}"
alt="{{ item.product.name }}"
>

<div style="flex:1">

<h3>
{{ item.product.name }}
</h3>

<p>
Quantity: {{ item.quantity }}
</p>

<p class="price">
৳{{ item.subtotal }}
</p>

</div>

<a class="btn"
href="/remove/{{ item.product.id }}">
Remove
</a>

</div>

{% else %}

<p>Your cart is empty.</p>

{% endfor %}

{% if total > 0 %}

<div class="cart-total">

Total:
<strong>৳{{ total }}</strong>

<br><br>

<a class="btn" href="/checkout">
CHECKOUT
</a>

</div>

{% endif %}

</div>

</section>
"""

    return render_template_string(
        BASE_HTML.replace("{% block_content %}", content),
        title="Cart",
        cart_data=cart_data,
        total=total
    )


# =========================================================
# CHECKOUT
# =========================================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    if request.method == "POST":

        if not session.get("cart"):
            return redirect(url_for("cart"))

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        payment = request.form.get("payment", "").strip()

        session["cart"] = {}

        content = """

<section class="section">

<div class="container">

<div class="form-box">

<h1>Order Confirmed ✓</h1>

<br>

<p>
Thank you <strong>{{ name }}</strong>.
</p>

<br>

<p>
Your order has been received successfully.
</p>

<br>

<p>
Phone: {{ phone }}
</p>

<p>
Payment: {{ payment }}
</p>

<p>
Address: {{ address }}
</p>

<br>

<a class="btn" href="/">
CONTINUE SHOPPING
</a>

</div>

</div>

</section>
"""

        return render_template_string(
            BASE_HTML.replace("{% block_content %}", content),
            title="Order Confirmed",
            name=name,
            phone=phone,
            payment=payment,
            address=address,
        )

    content = """

<section class="section">

<div class="container">

<div class="form-box">

<h2>Checkout</h2>

<form method="POST">

<label>Full Name</label>

<input
name="name"
required
placeholder="Your name"
>

<label>Phone Number</label>

<input
name="phone"
required
placeholder="01XXXXXXXXX"
>

<label>Delivery Address</label>

<textarea
name="address"
required
rows="4"
placeholder="Your complete address"
></textarea>

<label>Payment Method</label>

<select name="payment">

<option>Cash on Delivery</option>
<option>bKash</option>
<option>Nagad</option>
<option>Card</option>

</select>

<button class="btn" type="submit">
PLACE ORDER
</button>

</form>

</div>

</div>

</section>
"""

    return render_template_string(
        BASE_HTML.replace("{% block_content %}", content),
        title="Checkout"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
