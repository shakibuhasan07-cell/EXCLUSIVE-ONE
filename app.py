import os, re, sqlite3, secrets, time, smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from functools import wraps
from pathlib import Path
from flask import Flask, request, redirect, url_for, session, render_template, flash, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    MAX_CONTENT_LENGTH=3 * 1024 * 1024,
    PERMANENT_SESSION_LIFETIME=timedelta(days=14),
)
DATABASE = os.environ.get("DATABASE", str(BASE_DIR / "exclusive_one.db"))

CONTACT_PHONE = "+8801609228262"
CONTACT_EMAIL = "exclusiveone1@gmail.com"
INSTAGRAM = "exclusive_one1"
FACEBOOK = "Exclusive ONE"
PAYMENTS = {
    "bKash": "01609228262",
    "Nagad": "01609228262",
    "Rocket": "01632211644",
    "Bank Card": "Secure card gateway",
    "Cash on Delivery": "Pay when your order arrives",
}

PRODUCTS = [
    {"id":1,"name":"Premium Oversized T-Shirt","category":"Men","price":899,"old_price":1199,"stock":30,"sizes":"S,M,L,XL,XXL","image":"https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=1000","description":"Premium cotton oversized t-shirt with a clean modern fit."},
    {"id":2,"name":"Classic Black Shirt","category":"Men","price":1299,"old_price":1599,"stock":25,"sizes":"S,M,L,XL","image":"https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=1000","description":"Minimal classic shirt designed for smart casual looks."},
    {"id":3,"name":"Elegant Women's Dress","category":"Women","price":1899,"old_price":2299,"stock":18,"sizes":"S,M,L,XL","image":"https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=1000","description":"Elegant premium dress with a sophisticated aesthetic."},
    {"id":4,"name":"Premium Hand Bag","category":"Accessories","price":1599,"old_price":1999,"stock":20,"sizes":"Free Size","image":"https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=1000","description":"Stylish premium handbag suitable for everyday use."},
    {"id":5,"name":"Luxury Sunglasses","category":"Accessories","price":999,"old_price":1299,"stock":35,"sizes":"Free Size","image":"https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=1000","description":"Modern sunglasses with a premium luxury appearance."},
    {"id":6,"name":"Minimalist Watch","category":"Lifestyle","price":2199,"old_price":2799,"stock":12,"sizes":"Free Size","image":"https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=1000","description":"Minimalist watch designed for modern everyday style."},
    {"id":7,"name":"Premium Hoodie","category":"Men","price":1699,"old_price":2099,"stock":22,"sizes":"M,L,XL,XXL","image":"https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=1000","description":"Comfortable premium hoodie with a modern streetwear fit."},
    {"id":8,"name":"Women's Casual Top","category":"Women","price":1099,"old_price":1399,"stock":28,"sizes":"S,M,L,XL","image":"https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?w=1000","description":"Simple and elegant casual top for everyday fashion."},
    {"id":9,"name":"Kids Comfort Set","category":"Children","price":999,"old_price":1299,"stock":24,"sizes":"2Y,4Y,6Y,8Y,10Y","image":"https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=1000","description":"Comfortable everyday set designed for active kids."},
    {"id":10,"name":"Kids Casual Sneakers","category":"Children","price":1299,"old_price":1599,"stock":20,"sizes":"28,30,32,34,36","image":"https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=1000","description":"Lightweight casual sneakers for children."},
    {"id":11,"name":"Classic White Sneakers","category":"Shoes","price":1899,"old_price":2299,"stock":25,"sizes":"39,40,41,42,43,44","image":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1000","description":"Clean everyday sneakers with a versatile modern look."},
    {"id":12,"name":"Urban Running Shoes","category":"Shoes","price":2399,"old_price":2899,"stock":18,"sizes":"39,40,41,42,43,44","image":"https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=1000","description":"Comfort-focused running shoes for daily movement."},
    {"id":13,"name":"Wireless Earbuds","category":"Gadgets","price":1799,"old_price":2199,"stock":30,"sizes":"Free Size","image":"https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=1000","description":"Compact wireless earbuds for everyday listening."},
    {"id":14,"name":"Smart Watch Pro","category":"Gadgets","price":2999,"old_price":3599,"stock":15,"sizes":"Free Size","image":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1000","description":"Smart everyday watch with a clean premium design."},
]


def db():
    c = sqlite3.connect(DATABASE)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c


def column_exists(c, table, column):
    return any(r[1] == column for r in c.execute(f"PRAGMA table_info({table})").fetchall())


def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      email TEXT UNIQUE, phone TEXT UNIQUE, password TEXT NOT NULL,
      avatar TEXT DEFAULT '', is_admin INTEGER DEFAULT 0, verified INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      points INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS products(
      id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
      price INTEGER NOT NULL, old_price INTEGER DEFAULT 0, stock INTEGER DEFAULT 0,
      sizes TEXT DEFAULT 'Free Size', image TEXT, description TEXT, active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS wishlist(user_id INTEGER, product_id INTEGER, PRIMARY KEY(user_id, product_id));
    CREATE TABLE IF NOT EXISTS reviews(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, product_id INTEGER,
      rating INTEGER NOT NULL, comment TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(user_id, product_id)
    );
    CREATE TABLE IF NOT EXISTS coupons(code TEXT PRIMARY KEY, discount_percent INTEGER DEFAULT 0, active INTEGER DEFAULT 1, min_total INTEGER DEFAULT 0, expires_at TEXT);
    CREATE TABLE IF NOT EXISTS orders(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
      name TEXT NOT NULL, phone TEXT NOT NULL, address TEXT NOT NULL,
      payment TEXT NOT NULL, subtotal INTEGER NOT NULL, discount INTEGER DEFAULT 0,
      delivery INTEGER DEFAULT 0, total INTEGER NOT NULL, status TEXT DEFAULT 'Pending',
      transaction_id TEXT DEFAULT '', points_awarded INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS order_items(
      id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, product_id INTEGER,
      product_name TEXT, price INTEGER, quantity INTEGER, size TEXT DEFAULT 'Free Size'
    );
    CREATE TABLE IF NOT EXISTS tokens(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, kind TEXT, token TEXT UNIQUE,
      expires_at TEXT, used INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS contact_messages(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, phone TEXT, message TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP, handled INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS login_attempts(
      id INTEGER PRIMARY KEY AUTOINCREMENT, identifier TEXT, ip TEXT, success INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # Migrate older versions safely.
    for col, definition in [("phone", "TEXT UNIQUE"), ("avatar", "TEXT DEFAULT ''")]:
        if not column_exists(c, "users", col):
            try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
            except sqlite3.OperationalError: pass
    if not column_exists(c, "users", "points"):
        c.execute("ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0")
    if not column_exists(c, "orders", "points_awarded"):
        c.execute("ALTER TABLE orders ADD COLUMN points_awarded INTEGER DEFAULT 0")
    if not column_exists(c, "products", "sizes"):
        c.execute("ALTER TABLE products ADD COLUMN sizes TEXT DEFAULT 'Free Size'")
    if not column_exists(c, "order_items", "size"):
        c.execute("ALTER TABLE order_items ADD COLUMN size TEXT DEFAULT 'Free Size'")
    # Rebuild legacy cart table if necessary so size is part of an item identity.
    c.execute("""CREATE TABLE IF NOT EXISTS cart_items_v2(
        user_id INTEGER, product_id INTEGER, size TEXT DEFAULT 'Free Size', quantity INTEGER NOT NULL,
        PRIMARY KEY(user_id, product_id, size), FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    )""")
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    if "cart_items" in tables:
        cols = [r[1] for r in c.execute("PRAGMA table_info(cart_items)").fetchall()]
        if "size" not in cols:
            c.execute("INSERT OR IGNORE INTO cart_items_v2(user_id,product_id,size,quantity) SELECT user_id,product_id,'Free Size',quantity FROM cart_items")
            c.execute("DROP TABLE cart_items")
            c.execute("ALTER TABLE cart_items_v2 RENAME TO cart_items")
    else:
        c.execute("ALTER TABLE cart_items_v2 RENAME TO cart_items")
    for p in PRODUCTS:
        c.execute("""INSERT OR IGNORE INTO products(id,name,category,price,old_price,stock,sizes,image,description)
                     VALUES(?,?,?,?,?,?,?,?,?)""", (p["id"],p["name"],p["category"],p["price"],p["old_price"],p["stock"],p["sizes"],p["image"],p["description"]))
        c.execute("UPDATE products SET sizes=COALESCE(NULLIF(sizes,''),?) WHERE id=?", (p["sizes"],p["id"]))
    c.execute("INSERT OR IGNORE INTO coupons(code,discount_percent,min_total) VALUES('WELCOME10',10,1000)")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@exclusive-one.local").lower()
    admin_pass = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
    if not c.execute("SELECT id FROM users WHERE email=?", (admin_email,)).fetchone():
        c.execute("INSERT INTO users(name,email,password,is_admin,verified) VALUES(?,?,?,?,1)", ("EXCLUSIVE ONE Admin", admin_email, generate_password_hash(admin_pass), 1))
    c.commit(); c.close()

def migrate_legacy_v1():
    """Import V1 users/orders when a legacy users.db is placed beside app.py.
    Existing V3 records are never overwritten.
    """
    legacy = BASE_DIR / "users.db"
    if not legacy.exists() or legacy.resolve() == Path(DATABASE).resolve():
        return
    try:
        old = sqlite3.connect(str(legacy))
        old.row_factory = sqlite3.Row
        tables = {r[0] for r in old.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        with db() as c:
            if "users" in tables:
                for u in old.execute("SELECT * FROM users").fetchall():
                    email = (u["email"] or "").strip().lower() if "email" in u.keys() else ""
                    if not email:
                        continue
                    exists = c.execute("SELECT id FROM users WHERE lower(email)=?", (email,)).fetchone()
                    if not exists:
                        c.execute("INSERT INTO users(name,email,password,verified) VALUES(?,?,?,1)",
                                  ((u["name"] or "V1 User"), email, u["password"]))
            if "orders" in tables:
                cols = {r[1] for r in old.execute("PRAGMA table_info(orders)").fetchall()}
                if {"user_id","name","phone","address","payment","total"}.issubset(cols):
                    for o in old.execute("SELECT * FROM orders").fetchall():
                        old_uid = o["user_id"]
                        old_user = old.execute("SELECT email FROM users WHERE id=?", (old_uid,)).fetchone() if "users" in tables else None
                        if not old_user or not old_user["email"]:
                            continue
                        nu = c.execute("SELECT id FROM users WHERE lower(email)=?", (old_user["email"].lower(),)).fetchone()
                        if not nu:
                            continue
                        exists = c.execute("SELECT id FROM orders WHERE user_id=? AND name=? AND phone=? AND address=? AND total=? AND created_at=?",
                                           (nu["id"],o["name"],o["phone"],o["address"],o["total"],o["created_at"])).fetchone()
                        if not exists:
                            c.execute("INSERT INTO orders(user_id,name,phone,address,payment,subtotal,discount,delivery,total,status,created_at) VALUES(?,?,?,?,?,?,0,0,?, 'Pending', ?)",
                                      (nu["id"],o["name"],o["phone"],o["address"],o["payment"],o["total"],o["total"],o["created_at"]))
            c.commit()
        old.close()
    except Exception:
        try: old.close()
        except Exception: pass

migrate_legacy_v1()


init_db()


def csrf_token():
    if "csrf" not in session: session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def new_captcha():
    a, b = secrets.randbelow(8) + 2, secrets.randbelow(8) + 2
    session["captcha_answer"] = str(a + b)
    session["captcha_question"] = f"{a} + {b} = ?"


def captcha_ok(value):
    return secrets.compare_digest(str(value or "").strip(), str(session.get("captcha_answer", "")))


def valid_email(e): return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e or ""))
def valid_phone(p): return bool(re.match(r"^(?:\+?880|0)1[3-9]\d{8}$", re.sub(r"[\s-]", "", p or "")))
def normalize_phone(p):
    p = re.sub(r"[\s-]", "", p or "")
    if p.startswith("+880"): return "0" + p[4:]
    if p.startswith("880"): return "0" + p[3:]
    return p


def password_ok(p):
    return len(p) >= 8 and bool(re.search(r"[A-Za-z]", p)) and bool(re.search(r"\d", p))


def rate_limited(identifier):
    since = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
    with db() as c:
        n = c.execute("SELECT COUNT(*) n FROM login_attempts WHERE identifier=? AND ip=? AND success=0 AND created_at>=?", (identifier, request.remote_addr or "", since)).fetchone()["n"]
    return n >= 5


def record_attempt(identifier, success):
    with db() as c:
        c.execute("INSERT INTO login_attempts(identifier,ip,success) VALUES(?,?,?)", (identifier, request.remote_addr or "", int(success)))
        c.commit()


@app.context_processor
def globals():
    count = 0
    if session.get("user_id"):
        with db() as c:
            row = c.execute("SELECT COALESCE(SUM(quantity),0) n FROM cart_items WHERE user_id=?", (session["user_id"],)).fetchone()
            count = row["n"]
    else:
        count = sum(int(v) for v in session.get("cart", {}).values())
    points = 0
    if session.get("user_id"):
        with db() as c:
            points = c.execute("SELECT COALESCE(points,0) p FROM users WHERE id=?", (session["user_id"],)).fetchone()["p"]
    return {"csrf": csrf_token(), "cart_count": count, "current_user": session.get("user_name"), "current_points": points, "current_avatar": session.get("avatar", ""), "is_admin": session.get("is_admin", False), "contact_phone": CONTACT_PHONE, "contact_email": CONTACT_EMAIL, "instagram": INSTAGRAM, "facebook": FACEBOOK, "payments": PAYMENTS}


@app.before_request
def security():
    if request.method == "POST":
        sent = request.form.get("_csrf", "")
        if not secrets.compare_digest(sent, session.get("csrf", "")): abort(400, "Invalid form token.")
    session.permanent = True


@app.after_request
def headers(r):
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    r.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    r.headers["Content-Security-Policy"] = "default-src 'self' https:; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self' https:; frame-ancestors 'self'"
    return r


def login_required(f):
    @wraps(f)
    def w(*a, **kw):
        if not session.get("user_id"):
            flash("Please login first.", "warning"); return redirect(url_for("login", next=request.path))
        return f(*a, **kw)
    return w


def admin_required(f):
    @wraps(f)
    def w(*a, **kw):
        if not session.get("is_admin"): abort(403)
        return f(*a, **kw)
    return w


def get_product(pid):
    with db() as c: return c.execute("SELECT * FROM products WHERE id=? AND active=1", (pid,)).fetchone()


def size_list(product):
    return [x.strip() for x in (product["sizes"] or "Free Size").split(",") if x.strip()] or ["Free Size"]


def cart_rows(user_id=None):
    with db() as c:
        if user_id:
            rows = c.execute("""SELECT p.*, ci.size, ci.quantity, p.price*ci.quantity subtotal
                FROM cart_items ci JOIN products p ON p.id=ci.product_id
                WHERE ci.user_id=? AND p.active=1 ORDER BY ci.rowid DESC""", (user_id,)).fetchall()
        else:
            rows=[]
            for key,q in session.get("cart",{}).items():
                parts = str(key).split("|",1); pid=int(parts[0]); size=parts[1] if len(parts)>1 else "Free Size"
                p=c.execute("SELECT * FROM products WHERE id=? AND active=1", (pid,)).fetchone()
                if p: rows.append(dict(p)|{"size":size,"quantity":int(q),"subtotal":p["price"]*int(q)})
        return rows, sum(x["subtotal"] for x in rows)


def add_cart(pid, qty=1, size="Free Size"):
    p=get_product(pid)
    if not p or p["stock"] <= 0: return False, "Product unavailable."
    size=size.strip() or "Free Size"
    if size not in size_list(p): return False, "Please choose a valid size."
    qty=max(1,min(int(qty),p["stock"]))
    if session.get("user_id"):
        with db() as c:
            old=c.execute("SELECT quantity FROM cart_items WHERE user_id=? AND product_id=? AND size=?",(session["user_id"],pid,size)).fetchone()
            new=min(p["stock"],(old["quantity"] if old else 0)+qty)
            c.execute("INSERT INTO cart_items(user_id,product_id,size,quantity) VALUES(?,?,?,?) ON CONFLICT(user_id,product_id,size) DO UPDATE SET quantity=excluded.quantity",(session["user_id"],pid,size,new)); c.commit()
    else:
        cart=session.get("cart",{}); key=f"{pid}|{size}"; cart[key]=min(p["stock"],int(cart.get(key,0))+qty); session["cart"]=cart
    return True,"Added to cart."


def merge_guest_cart(user_id):
    guest=session.pop("cart",{})
    for key,q in guest.items():
        parts=str(key).split("|",1); pid=int(parts[0]); size=parts[1] if len(parts)>1 else "Free Size"
        try: add_cart(pid,int(q),size)
        except Exception: pass


def send_email(to, subject, body):
    host=os.environ.get("SMTP_HOST"); port=int(os.environ.get("SMTP_PORT","587")); user=os.environ.get("SMTP_USER"); password=os.environ.get("SMTP_PASSWORD"); sender=os.environ.get("SMTP_FROM",user or CONTACT_EMAIL)
    if not host or not user or not password: return False
    try:
        msg=EmailMessage(); msg["Subject"]=subject; msg["From"]=sender; msg["To"]=to; msg.set_content(body)
        with smtplib.SMTP(host,port,timeout=10) as s:
            s.starttls(); s.login(user,password); s.send_message(msg)
        return True
    except Exception:
        return False


@app.route("/")
def home():
    with db() as c: products=c.execute("SELECT * FROM products WHERE active=1 ORDER BY id DESC LIMIT 12").fetchall()
    return render_template("home.html",products=products)


@app.route("/shop")
def shop():
    q=request.args.get("q","").strip(); cat=request.args.get("category","").strip(); sort=request.args.get("sort","latest")
    sql="SELECT * FROM products WHERE active=1"; args=[]
    if q: sql+=" AND (name LIKE ? OR category LIKE ? OR description LIKE ?)"; args += [f"%{q}%"]*3
    if cat: sql+=" AND category=?"; args.append(cat)
    sql += {"price_low":" ORDER BY price ASC","price_high":" ORDER BY price DESC","name":" ORDER BY name ASC"}.get(sort," ORDER BY id DESC")
    with db() as c: products=c.execute(sql,args).fetchall()
    with db() as c: categories=[r[0] for r in c.execute("SELECT DISTINCT category FROM products WHERE active=1 ORDER BY category").fetchall()]
    return render_template("shop.html",products=products,q=q,category=cat,sort=sort,categories=categories)


@app.route("/product/<int:pid>",methods=["GET","POST"])
def product(pid):
    p=get_product(pid)
    if not p: abort(404)
    if request.method=="POST":
        if not session.get("user_id"): return redirect(url_for("login",next=request.path))
        rating=max(1,min(5,int(request.form.get("rating",5)))); comment=request.form.get("comment","").strip()[:1000]
        with db() as c:
            c.execute("INSERT INTO reviews(user_id,product_id,rating,comment) VALUES(?,?,?,?) ON CONFLICT(user_id,product_id) DO UPDATE SET rating=excluded.rating,comment=excluded.comment",(session["user_id"],pid,rating,comment)); c.commit()
        flash("Review saved.","success"); return redirect(request.path)
    with db() as c:
        reviews=c.execute("SELECT r.*,u.name FROM reviews r LEFT JOIN users u ON u.id=r.user_id WHERE r.product_id=? ORDER BY r.id DESC",(pid,)).fetchall()
        avg=c.execute("SELECT COALESCE(AVG(rating),0) a FROM reviews WHERE product_id=?",(pid,)).fetchone()["a"]
    return render_template("product.html",product=p,reviews=reviews,avg=round(avg,1),sizes=size_list(p))


@app.post("/buy-now/<int:pid>")
def buy_now(pid):
    if not session.get("user_id"):
        return redirect(url_for("login", next=url_for("product", pid=pid)))
    ok,msg=add_cart(pid,request.form.get("quantity",1),request.form.get("size","Free Size")); flash(msg,"success" if ok else "danger")
    return redirect(url_for("checkout" if ok else "product", pid=pid) if not ok else url_for("checkout"))


@app.post("/cart/add/<int:pid>")
def cart_add(pid):
    ok,msg=add_cart(pid,request.form.get("quantity",1),request.form.get("size","Free Size")); flash(msg,"success" if ok else "danger")
    if ok and request.form.get("action")=="buy": return redirect(url_for("checkout"))
    return redirect(request.referrer or url_for("cart"))


@app.post("/cart/update")
def cart_update():
    with db() as c:
        if session.get("user_id"):
            for key,val in request.form.items():
                if not key.startswith("qty_"): continue
                _,pid,size=key.split("_",2); qty=max(0,int(val)); p=get_product(int(pid))
                if not p: continue
                if qty==0: c.execute("DELETE FROM cart_items WHERE user_id=? AND product_id=? AND size=?",(session["user_id"],pid,size))
                else: c.execute("UPDATE cart_items SET quantity=? WHERE user_id=? AND product_id=? AND size=?",(min(qty,p["stock"]),session["user_id"],pid,size))
            c.commit()
        else:
            cart=session.get("cart",{})
            for key,val in request.form.items():
                if key.startswith("qty_"):
                    k=key[4:]; q=max(0,int(val));
                    if q: cart[k]=q
                    else: cart.pop(k,None)
            session["cart"]=cart
    return redirect(url_for("cart"))


@app.post("/cart/remove")
def cart_remove():
    pid=int(request.form.get("pid",0)); size=request.form.get("size","Free Size")
    if session.get("user_id"):
        with db() as c: c.execute("DELETE FROM cart_items WHERE user_id=? AND product_id=? AND size=?",(session["user_id"],pid,size)); c.commit()
    else:
        cart=session.get("cart",{}); cart.pop(f"{pid}|{size}",None); session["cart"]=cart
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    rows,total=cart_rows(session.get("user_id")); return render_template("cart.html",rows=rows,total=total)


# V1 compatibility routes. They keep old bookmarks/links working while using V3 security.
@app.post("/add/<int:product_id>")
def legacy_add(product_id):
    ok, msg = add_cart(product_id, 1, request.form.get("size", "Free Size"))
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("cart"))

@app.post("/remove/<int:product_id>")
def legacy_remove(product_id):
    rows, _ = cart_rows(session.get("user_id"))
    matches = [r for r in rows if int(r["id"]) == product_id]
    if session.get("user_id"):
        with db() as c:
            c.execute("DELETE FROM cart_items WHERE user_id=? AND product_id=?", (session["user_id"], product_id)); c.commit()
    else:
        cart=session.get("cart", {})
        for k in list(cart):
            if str(k).split("|",1)[0] == str(product_id): cart.pop(k,None)
        session["cart"]=cart
    flash("Product removed from cart.", "info")
    return redirect(url_for("cart"))


@app.post("/wishlist/<int:pid>")
@login_required
def wishlist_toggle(pid):
    with db() as c:
        exists=c.execute("SELECT 1 FROM wishlist WHERE user_id=? AND product_id=?",(session["user_id"],pid)).fetchone()
        if exists: c.execute("DELETE FROM wishlist WHERE user_id=? AND product_id=?",(session["user_id"],pid)); flash("Removed from wishlist.","info")
        else: c.execute("INSERT OR IGNORE INTO wishlist(user_id,product_id) VALUES(?,?)",(session["user_id"],pid)); flash("Added to wishlist.","success")
        c.commit()
    return redirect(request.referrer or url_for("wishlist"))


@app.route("/wishlist")
@login_required
def wishlist():
    with db() as c: products=c.execute("SELECT p.* FROM wishlist w JOIN products p ON p.id=w.product_id WHERE w.user_id=? AND p.active=1 ORDER BY w.rowid DESC",(session["user_id"],)).fetchall()
    return render_template("wishlist.html",products=products)


@app.route("/checkout",methods=["GET","POST"])
@login_required
def checkout():
    rows,subtotal=cart_rows(session["user_id"])
    if not rows: return redirect(url_for("cart"))
    with db() as c:
        u=c.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone()
        has_previous=c.execute("SELECT 1 FROM orders WHERE user_id=? AND status!='Cancelled' LIMIT 1",(session["user_id"],)).fetchone() is not None
    def calc(coupon_code="", district="", points_used=0):
        coupon_discount=0; next_discount=0
        with db() as c:
            if coupon_code:
                cp=c.execute("SELECT * FROM coupons WHERE code=? AND active=1",(coupon_code.upper(),)).fetchone()
                if cp and subtotal>=cp["min_total"] and (not cp["expires_at"] or cp["expires_at"]>=datetime.utcnow().isoformat()):
                    coupon_discount=subtotal*cp["discount_percent"]//100
        base=max(0,subtotal-coupon_discount)
        if has_previous and not coupon_code: next_discount=base*10//100
        points_used=max(0,min(int(points_used or 0),int(u["points"] or 0)))
        points_discount=max(0,base-next_discount)*points_used//100
        after=max(0,base-next_discount-points_discount)
        delivery=0 if after>=2999 else (60 if district.lower() in {"dhaka","ঢাকা","dhaka city","dhaka metropolitan"} else 120)
        return coupon_discount,next_discount,points_used,points_discount,delivery,after+delivery
    if request.method=="POST":
        name=request.form.get("name","").strip(); phone=normalize_phone(request.form.get("phone","")); address=request.form.get("address","").strip(); district=request.form.get("district","").strip(); payment=request.form.get("payment","").strip(); tx=request.form.get("transaction_id","").strip()[:80]; coupon=request.form.get("coupon","").strip().upper()
        try: points_used=int(request.form.get("points_used","0") or 0)
        except ValueError: points_used=0
        if len(name)<2 or not valid_phone(phone) or len(address)<8 or not district or payment not in PAYMENTS:
            flash("Please complete your delivery address and payment information.","danger")
            return render_template("checkout.html",rows=rows,subtotal=subtotal,user=u,has_previous=has_previous,**dict(zip(["coupon_discount","next_discount","points_used","points_discount","delivery","total"],calc(coupon,district,points_used))))
        coupon_discount,next_discount,points_used,points_discount,delivery,total=calc(coupon,district,points_used)
        with db() as c:
            for r in rows:
                p=c.execute("SELECT stock FROM products WHERE id=? AND active=1",(r["id"],)).fetchone()
                if not p or p["stock"]<r["quantity"]:
                    flash(f"Not enough stock for {r['name']}.","danger"); return render_template("checkout.html",rows=rows,subtotal=subtotal,user=u,has_previous=has_previous,coupon_discount=coupon_discount,next_discount=next_discount,points_used=points_used,points_discount=points_discount,delivery=delivery,total=total)
            earned=max(1, subtotal//500) + (10 if total>=2999 else 0)
            discount=coupon_discount+next_discount+points_discount
            cur=c.execute("INSERT INTO orders(user_id,name,phone,address,payment,subtotal,discount,delivery,total,transaction_id,points_awarded) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(session["user_id"],name,phone,f"{address}, {district}",payment,subtotal,discount,delivery,total,tx,earned))
            oid=cur.lastrowid
            for r in rows:
                c.execute("INSERT INTO order_items(order_id,product_id,product_name,price,quantity,size) VALUES(?,?,?,?,?,?)",(oid,r["id"],r["name"],r["price"],r["quantity"],r["size"]))
                c.execute("UPDATE products SET stock=stock-? WHERE id=?",(r["quantity"],r["id"]))
            c.execute("UPDATE users SET points=MAX(0,COALESCE(points,0)-?)+? WHERE id=?",(points_used,earned,session["user_id"]))
            c.execute("DELETE FROM cart_items WHERE user_id=?",(session["user_id"],)); c.commit()
        flash(f"Order placed successfully! You earned {earned} Exclusive Points.","success")
        return redirect(url_for("order_detail",oid=oid))
    coupon_discount,next_discount,points_used,points_discount,delivery,total=calc()
    return render_template("checkout.html",rows=rows,subtotal=subtotal,user=u,has_previous=has_previous,coupon_discount=coupon_discount,next_discount=next_discount,points_used=points_used,points_discount=points_discount,delivery=delivery,total=total)


@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        if not captcha_ok(request.form.get("captcha")): flash("Captcha answer is incorrect.","danger"); new_captcha(); return render_template("signup.html")
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower() or None; phone=normalize_phone(request.form.get("phone","")); pw=request.form.get("password","")
        if email and not valid_email(email): email=None
        if not email and not valid_phone(phone): flash("Enter a valid email or Bangladesh mobile number.","danger"); new_captcha(); return render_template("signup.html")
        if not password_ok(pw): flash("Password must be 8+ characters and include letters and numbers.","danger"); new_captcha(); return render_template("signup.html")
        with db() as c:
            if (email and c.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone()) or (phone and c.execute("SELECT id FROM users WHERE phone=?",(phone,)).fetchone()): flash("That email or phone is already registered.","danger"); new_captcha(); return render_template("signup.html")
            internal_email=email or f"{phone}@phone.exclusive-one.local"
            c.execute("INSERT INTO users(name,email,phone,password,verified) VALUES(?,?,?,?,?)",(name,internal_email,phone or None,generate_password_hash(pw),1)); c.commit()
        flash("Account created successfully. Please login.","success"); return redirect(url_for("login"))
    new_captcha(); return render_template("signup.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        identifier=request.form.get("identifier","").strip().lower(); pw=request.form.get("password","")
        if not captcha_ok(request.form.get("captcha")): flash("Captcha answer is incorrect.","danger"); new_captcha(); return render_template("login.html")
        if rate_limited(identifier): flash("Too many failed attempts. Try again in 10 minutes.","danger"); new_captcha(); return render_template("login.html")
        phone=normalize_phone(identifier)
        with db() as c: u=c.execute("SELECT * FROM users WHERE lower(email)=? OR phone=?",(identifier,phone)).fetchone()
        if not u or not check_password_hash(u["password"],pw): record_attempt(identifier,False); flash("Invalid login details.","danger"); new_captcha(); return render_template("login.html")
        record_attempt(identifier,True); session.clear(); session["csrf"]=secrets.token_urlsafe(32); session["user_id"]=u["id"]; session["user_name"]=u["name"]; session["avatar"]=u["avatar"] or ""; session["is_admin"]=bool(u["is_admin"]); merge_guest_cart(u["id"])
        return redirect(request.args.get("next") or url_for("dashboard"))
    new_captcha(); return render_template("login.html")


@app.post("/logout")
def logout(): session.clear(); flash("Logged out.","info"); return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    with db() as c: orders=c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 5",(session["user_id"],)).fetchall()
    return render_template("dashboard.html",orders=orders)


@app.route("/profile",methods=["GET","POST"])
@login_required
def profile():
    if request.method=="POST":
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower(); phone=normalize_phone(request.form.get("phone",""))
        if len(name)<2 or (email and not valid_email(email)) or (phone and not valid_phone(phone)): flash("Please enter valid profile information.","danger")
        else:
            with db() as c:
                try:
                    old_email=c.execute("SELECT email FROM users WHERE id=?",(session["user_id"],)).fetchone()[0]
                    c.execute("UPDATE users SET name=?,email=?,phone=? WHERE id=?",(name,email or old_email,phone or None,session["user_id"]))
                    c.commit(); session["user_name"]=name; flash("Profile updated.","success")
                except sqlite3.IntegrityError: flash("Email or phone is already used by another account.","danger")
        return redirect(request.path)
    with db() as c: u=c.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone()
    return render_template("profile.html",user=u)


@app.post("/profile/avatar")
@login_required
def profile_avatar():
    f=request.files.get("avatar")
    if not f or not f.filename: flash("Choose a profile picture.","danger"); return redirect(url_for("profile"))
    ext=Path(secure_filename(f.filename)).suffix.lower()
    if ext not in {".jpg",".jpeg",".png",".webp"}: flash("Use JPG, PNG or WEBP only.","danger"); return redirect(url_for("profile"))
    data=f.read()
    if len(data)>2*1024*1024: flash("Profile picture must be under 2 MB.","danger"); return redirect(url_for("profile"))
    if not ((data.startswith(b"\xff\xd8\xff") and ext in {".jpg",".jpeg"}) or (data.startswith(b"\x89PNG\r\n\x1a\n") and ext==".png") or (data[:12].startswith(b"RIFF") and data[8:12]==b"WEBP" and ext==".webp")):
        flash("The uploaded file is not a valid supported image.","danger"); return redirect(url_for("profile"))
    filename=f"avatar_{session['user_id']}_{secrets.token_hex(8)}{ext}"; (UPLOAD_DIR/filename).write_bytes(data)
    with db() as c: c.execute("UPDATE users SET avatar=? WHERE id=?",(filename,session["user_id"])); c.commit()
    session["avatar"]=filename; flash("Profile picture updated.","success"); return redirect(url_for("profile"))


@app.route("/orders")
@login_required
def orders():
    with db() as c: data=c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC",(session["user_id"],)).fetchall()
    return render_template("orders.html",orders=data)


@app.route("/order/<int:oid>")
@login_required
def order_detail(oid):
    with db() as c:
        o=c.execute("SELECT * FROM orders WHERE id=? AND user_id=?",(oid,session["user_id"])).fetchone(); items=c.execute("SELECT * FROM order_items WHERE order_id=?",(oid,)).fetchall()
    if not o: abort(404)
    return render_template("order_detail.html",order=o,items=items)


@app.route("/forgot",methods=["GET","POST"])
def forgot():
    if request.method=="POST":
        if not captcha_ok(request.form.get("captcha")): flash("Captcha answer is incorrect.","danger"); new_captcha(); return render_template("forgot.html")
        identifier=request.form.get("identifier","").strip().lower(); phone=normalize_phone(identifier)
        with db() as c: u=c.execute("SELECT * FROM users WHERE lower(email)=? OR phone=?",(identifier,phone)).fetchone()
        # Always show a neutral message so account existence is not disclosed.
        if u:
            token=secrets.token_urlsafe(32)
            with db() as c: c.execute("INSERT INTO tokens(user_id,kind,token,expires_at) VALUES(?,?,?,?)",(u["id"],"reset",token,(datetime.utcnow()+timedelta(minutes=30)).isoformat())); c.commit()
            link=url_for("reset",token=token,_external=True)
            sent=False
            if u["email"] and "@phone.exclusive-one.local" not in u["email"]: sent=send_email(u["email"],"EXCLUSIVE ONE password reset",f"Reset your password within 30 minutes:\n{link}")
            if sent: flash("If the account exists, a password reset email has been sent.","success"); return render_template("forgot.html",dev_link=None)
            flash("Reset request created. For this local version, use the secure reset link below.","info"); return render_template("forgot.html",dev_link=link)
        flash("If the account exists, reset instructions will be provided.","info")
    new_captcha(); return render_template("forgot.html")


@app.route("/reset/<token>",methods=["GET","POST"])
def reset(token):
    with db() as c: t=c.execute("SELECT * FROM tokens WHERE token=? AND kind='reset' AND used=0",(token,)).fetchone()
    if not t or t["expires_at"]<datetime.utcnow().isoformat(): abort(400)
    if request.method=="POST":
        pw=request.form.get("password","")
        if not password_ok(pw): flash("Password must be 8+ characters and include letters and numbers.","danger")
        else:
            with db() as c: c.execute("UPDATE users SET password=? WHERE id=?",(generate_password_hash(pw),t["user_id"])); c.execute("UPDATE tokens SET used=1 WHERE id=?",(t["id"],)); c.commit()
            flash("Password reset successful.","success"); return redirect(url_for("login"))
    return render_template("reset.html")


@app.route("/contact",methods=["GET","POST"])
def contact():
    if request.method=="POST":
        name=request.form.get("name","").strip()[:80]; email=request.form.get("email","").strip().lower()[:120]; phone=normalize_phone(request.form.get("phone","")); message=request.form.get("message","").strip()[:2000]
        if not name or not message or (email and not valid_email(email)): flash("Please complete the form correctly.","danger")
        else:
            with db() as c: c.execute("INSERT INTO contact_messages(name,email,phone,message) VALUES(?,?,?,?)",(name,email,phone,message)); c.commit()
            send_email(CONTACT_EMAIL,"EXCLUSIVE ONE customer message",f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\n{message}")
            flash("Thanks! Your message has been sent to EXCLUSIVE ONE support.","success"); return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/about")
def about(): return render_template("simple.html",title="About EXCLUSIVE ONE",body="EXCLUSIVE ONE is a modern single-seller shopping platform bringing fashion, children's products, shoes, gadgets and lifestyle essentials together in one polished experience. We focus on quality, transparent pricing, secure account handling and responsive customer support. Every part of the store is designed to make discovering products and placing an order simple on both mobile and desktop.")
@app.route("/faq")
def faq(): return render_template("simple.html",title="FAQ",body="You can create an account with either an email address or a Bangladesh mobile number. Login and password recovery also support either identifier. Product pages show available sizes where applicable. For order support, contact us by WhatsApp, email or the Contact page.")
@app.route("/shipping")
def shipping(): return render_template("simple.html",title="Shipping",body="Inside Dhaka delivery is ৳60 and outside Dhaka is ৳120. Orders of ৳2,999 or more receive FREE home delivery anywhere in Bangladesh. Delivery timing can vary by location and product availability. We will contact you when needed to confirm your order.")
@app.route("/returns")
def returns(): return render_template("simple.html",title="Returns & Refunds",body="Contact EXCLUSIVE ONE support with your order number and reason. Products should be unused and in acceptable original condition. Eligibility depends on product category and order status.")
@app.route("/privacy")
def privacy(): return render_template("simple.html",title="Privacy & Security",body="EXCLUSIVE ONE uses password hashing, CSRF protection, secure session cookies, security headers, login throttling, input validation and safe file handling. We do not store raw bank-card numbers. Account and delivery information is used to operate the store and fulfill orders.")
@app.route("/terms")
def terms(): return render_template("simple.html",title="Terms & Conditions",body="By using EXCLUSIVE ONE you agree to provide accurate account and delivery information, use payment services lawfully and respect the store's product, delivery and return policies.")


@app.route("/rewards")
@login_required
def rewards():
    with db() as c:
        u=c.execute("SELECT points,name FROM users WHERE id=?",(session["user_id"],)).fetchone()
        earned=c.execute("SELECT COALESCE(SUM(points_awarded),0) n FROM orders WHERE user_id=?",(session["user_id"],)).fetchone()["n"]
        recent=c.execute("SELECT id,total,points_awarded,created_at,status FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 8",(session["user_id"],)).fetchall()
    return render_template("rewards.html",user=u,earned=earned,recent=recent)


@app.route("/admin")
@admin_required
def admin():
    with db() as c:
        stats={"users":c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"],"orders":c.execute("SELECT COUNT(*) n FROM orders").fetchone()["n"],"sales":c.execute("SELECT COALESCE(SUM(total),0) n FROM orders WHERE status!='Cancelled'").fetchone()["n"],"products":c.execute("SELECT COUNT(*) n FROM products WHERE active=1").fetchone()["n"]}
        recent=c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 10").fetchall()
    return render_template("admin.html",stats=stats,recent=recent)


@app.route("/admin/products",methods=["GET","POST"])
@admin_required
def admin_products():
    if request.method=="POST":
        name=request.form.get("name","").strip(); cat=request.form.get("category","Men"); price=int(request.form.get("price",0) or 0); old=int(request.form.get("old_price",0) or 0); stock=int(request.form.get("stock",0) or 0); sizes=request.form.get("sizes","Free Size").strip(); image=request.form.get("image","").strip(); desc=request.form.get("description","").strip()
        if name and price>0 and stock>=0:
            with db() as c: c.execute("INSERT INTO products(name,category,price,old_price,stock,sizes,image,description) VALUES(?,?,?,?,?,?,?,?)",(name,cat,price,old,stock,sizes,image,desc)); c.commit()
            flash("Product added successfully.","success")
        else: flash("Please enter valid product details.","danger")
        return redirect(request.path)
    with db() as c: products=c.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return render_template("admin_products.html",products=products)


@app.post("/admin/products/<int:pid>/delete")
@admin_required
def admin_delete_product(pid):
    with db() as c: c.execute("UPDATE products SET active=0 WHERE id=?",(pid,)); c.commit()
    flash("Product hidden.","info"); return redirect(url_for("admin_products"))


@app.post("/admin/order/<int:oid>/status")
@admin_required
def admin_order_status(oid):
    status=request.form.get("status","Pending")
    if status not in {"Pending","Confirmed","Processing","Shipped","Delivered","Cancelled"}: abort(400)
    with db() as c: c.execute("UPDATE orders SET status=? WHERE id=?",(status,oid)); c.commit()
    return redirect(url_for("admin"))


@app.errorhandler(404)
def e404(e): return render_template("error.html",code=404,message="Page not found."),404
@app.errorhandler(403)
def e403(e): return render_template("error.html",code=403,message="Access denied."),403
@app.errorhandler(400)
def e400(e): return render_template("error.html",code=400,message=str(e)),400
@app.errorhandler(413)
def e413(e): return render_template("error.html",code=413,message="Uploaded file is too large."),413

if __name__=="__main__":
    app.run(host=os.environ.get("HOST","127.0.0.1"),port=int(os.environ.get("PORT","5000")),debug=False)
