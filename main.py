from email.policy import default
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import datetime, date
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    current_user,
    login_user,
    logout_user,
)
from numpy import product
from werkzeug.utils import secure_filename
from PIL import Image
import pymysql
from sqlalchemy.sql import func

pymysql.install_as_MySQLdb()
from sqlalchemy import and_, or_, not_
import auth
from flask_cors import CORS
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_mail import Mail, Message

app = Flask(__name__)
app.config[
    "SECRET_KEY"
] = "Ywurow503985403924482jfsoakldfjasdltu394qipoafjo48950wjsfpas;lkr04589"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USERNAME"] = "kamrankhan567855@gmail.com"
app.config[
    "MAIL_PASSWORD"
] = "Kamrankhan0078900"  # use app password, you can create app password through google
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USE_TLS"] = False

mail = Mail(app)


db = SQLAlchemy(app)
Migrate(app, db)
CORS(app)
login_manager = LoginManager()

now = datetime.now()
login_manager.init_app(app)
login_manager.login_view = "login"
admin = Admin(app)


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


# Products (id, name, description, category, stock,
# created, modified, unit_price, visibility [true, false])

basdir = os.path.abspath(os.path.dirname(__file__))
Upload_dir = basdir + "/static/images/"
Allowed = ["JPG", "jpj", "PNG", "png"]


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(100), default="user")
    product = db.relationship("Orders", backref="user", lazy=True)
    rating = db.relationship("Ratings", backref="user", lazy=True)
    visibility = db.Column(db.String(255), default="True")


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    additional_description = db.Column(db.String(1000))
    category = db.Column(db.String(255), nullable=False)
    sub_category = db.Column(db.String(255))
    sub_cat_size = db.Column(db.String(255), default="")
    sub_cat_gender = db.Column(db.String(255), default="")
    sub_cat_homo = db.Column(db.String(255), default="")
    sub_cat_albino = db.Column(db.String(255), default="")
    sub_cat_melanoid = db.Column(db.String(255), default="")
    sub_cat_leucistic = db.Column(db.String(255), default="")
    sub_cat_wild = db.Column(db.String(255), default="")
    sub_cat_heter = db.Column(db.String(255), default="")
    stock = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.Boolean(), default=1)
    image = db.Column(db.String(255))
    created = db.Column(db.TIMESTAMP(), server_default=func.now())
    modified = db.Column(
        db.TIMESTAMP(), server_default=func.now(), onupdate=func.current_timestamp()
    )
    owner_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    orderitems = db.relationship("OrderItems", backref="products", lazy=True)
    rating = db.relationship("Ratings", backref="products", lazy=True)
    tags = db.Column(db.String(255))


# Orders table (id, user_id, created, total_price, address,
# payment_method, money_received)
class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    total_price = db.Column(db.Integer)
    address = db.Column(db.String(500))
    payment_method = db.Column(db.String(255))
    money_received = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=date.today())
    orderitems = db.relationship("OrderItems", backref="orders", lazy=True)


# OrderItems table (id, order_id, product_id, quantity, unit_price)


class OrderItems(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Integer)


# d Ratings (id, product_id, user_id, rating, comment,
# created, modified)
class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(255))
    created = db.Column(db.TIMESTAMP(), server_default=func.now())
    modified = db.Column(
        db.TIMESTAMP(), server_default=func.now(), onupdate=func.current_timestamp()
    )


def MergeDict(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))


@app.route("/")
def Home():
    try:
        cart_data = session["SHOP"]
    except:
        cart_data = {}
    row_per_page = 10
    page = request.args.get("page", 1, type=int)
    product = Products.query.paginate(page=page, per_page=row_per_page)
    return render_template(
        "index.html", product=product, cart_data=cart_data, category="home"
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if auth.verify(password, user.password):
                login_user(user)
                return redirect("/")
            else:
                flash("Incorrect Password!")
                return redirect("/login")
        else:
            flash("No User found with this Email")
            return redirect("/login")
    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def singup():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        email = request.form.get("email")
        password = request.form.get("password")
        r_password = request.form.get("r_password")

        user = User.query.filter_by(name="Admin", email="admin@gmail.com").first()

        if not user:
            hashed_password_admin = auth.hash("a@#$)($#$*admin@3435(*$%")
            admin = User(
                name="Admin",
                email="admin@gmail.com",
                password=hashed_password_admin,
                role="admin",
            )

            db.session.add(admin)
            db.session.commit()

        if not user_name:
            return {"name_err": "Name is required"}

        if not password:
            return {"password": "Password required"}
        if password != r_password:
            return {"password": "password not matched"}
        user = User.query.filter_by(name=user_name).first()

        if user:
            return {"user": "User Already Exists!"}
        email_checkup = User.query.filter_by(email=email).first()

        if email_checkup:
            return {"email": "Email Already Exists!"}

        print("done1")
        hashed_password = auth.hash(password)
        user_to_add = User(
            name=user_name,
            email=email,
            password=hashed_password,
        )
        db.session.add(user_to_add)
        db.session.commit()
        return {"msg": "created"}
    return render_template("signup.html")


@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.name != "Admin" or current_user.email != "admin@gmail.com":
        flash("Please login as a admin to Access this page")
        return redirect("/login")
    product = Products.query.all()
    cat = "dashboard"
    return render_template("dashboard/index.html", product=product, cat=cat)


@app.route("/add_post", methods=["GET", "POST"])
@login_required
def add_post():
    if current_user.name != "Admin" and current_user.email != "admin@gmail.com":
        flash("Please login as a admin to Access this page")
        return redirect("/login")
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        additional_description = request.form.get("additional_description")
        category = request.form.get("category")
        sub_category = request.form.get("sub-category")
        stock = request.form.get("stock")
        unit_price = request.form.get("unit_price")
        visibility = request.form.get("visibility")
        tag = request.form.get("tags")
        file = request.files["image"]
        filename = secure_filename(file.filename)

        if category == "Axolotls":
            size = request.form.get("size")
            gender = request.form.get("gender")
            homozygous = request.form.get("homozygous")
            heterozygous = request.form.get("heterozygous")

            albino = ""
            melanoid = ""
            leucistic = ""
            wild = ""
            if homozygous == "Albino":
                albino = request.form.get("albino")

            if homozygous == "Melanoid":
                melanoid = request.form.get("melanoid")

            if homozygous == "Leucistic":
                leucistic = request.form.get("leucistic")

            if homozygous == "Wild":
                wild = request.form.get("wild")



            if visibility.lower() == "true":
                visibility = 1
            else:
                visibility = 0
            data = Products(
                name=name,
                description=description,
                additional_description=additional_description,
                category=category,
                sub_category=sub_category,
                sub_cat_size=size,
                sub_cat_gender=gender,
                sub_cat_homo = homozygous,
                sub_cat_albino = albino,
                sub_cat_melanoid = melanoid,
                sub_cat_leucistic = leucistic,
                sub_cat_wild = wild,
                sub_cat_heter = heterozygous,
                stock=stock,
                unit_price=unit_price,
                visibility=visibility,
                image=filename,
                owner_id=current_user.id,
                tags=tag,
            )

            print(filename.split(".")[1])
            if str(filename.split(".")[1]) not in Allowed:
                flash(
                    "Our website does not support that type of extension, Please update your Product Image"
                )
            file.save(os.path.join(Upload_dir, filename))
            print(file)
            db.session.add(data)
            db.session.commit()
            return redirect("/add_post")

        else:

            if visibility.lower() == "true":
                visibility = 1
            else:
                visibility = 0
            data = Products(
                name=name,
                description=description,
                additional_description=additional_description,
                category=category,
                sub_category=sub_category,
                stock=stock,
                unit_price=unit_price,
                visibility=visibility,
                image=filename,
                owner_id=current_user.id,
                tags=tag,
            )

            print(filename.split(".")[1])
            if str(filename.split(".")[1]) not in Allowed:
                flash(
                    "Our website does not support that type of extension, Please update your Product Image"
                )
            file.save(os.path.join(Upload_dir, filename))
            print(file)
            db.session.add(data)
            db.session.commit()
            return redirect("/add_post")
            # print(name,description, stock, unit_price, visibility)
    return render_template("dashboard/pages/tables.html", cat="add_post")


@app.route("/delete/<id>")
@login_required
def delete_item(id):
    product = Products.query.filter_by(id=id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect("/admin_dashboard")


@app.route("/shop")
def shop():
    try:
        cart_data = session["SHOP"]
    except:
        cart_data = {}
    row_per_page = 10
    page = request.args.get("page", 1, type=int)
    product = Products.query.paginate(page=page, per_page=row_per_page)

    plushies = Products.query.filter_by(category="Plushies").all()
    Handmade = Products.query.filter_by(category="Handmade").all()
    Swag = Products.query.filter_by(category="Swag").all()
    Axolotls = Products.query.filter_by(category = "Axolotls").all()
    return render_template(
        "shop.html",
        product=product,
        cart_data=cart_data,
        plushies=plushies,
        handmade=Handmade,
        swag=Swag,
        axolotls = Axolotls,
        category="shop",
    )

@app.route("/filter", methods =["POST"])
def filter():
    size = request.form.get('size')
    gender = request.form.get('gender')
    homo = request.form.get('homo')
    albino = request.form.get('albino')
    melanoid = request.form.get('melanoid')
    leucistic = request.form.get('leucistic')
    wild = request.form.get('wild')
    heter = request.form.get('heter')


    row_per_page = 10
    page = request.args.get("page", 1, type=int)

    query = ""
    if albino == "" and melanoid == "" and leucistic == "":
        print('wild is running')
        print(wild)
        product = Products.query.filter_by(sub_cat_size=size,sub_cat_gender=gender,sub_cat_homo=homo,sub_cat_wild=wild).paginate(
        page=page, per_page=row_per_page)
        print(query)
        for data in query:
            print(data)
    if melanoid == "" and leucistic == "" and wild == "":
        print("albino is running")
        print(albino)
        product = Products.query.filter_by(sub_cat_size=size,sub_cat_gender=gender,sub_cat_homo=homo,sub_cat_albino = albino).paginate(
        page=page, per_page=row_per_page)

    if albino == "" and leucistic == "" and wild == "":
        print("melanoid is running")
        print(melanoid)
        product = Products.query.filter_by(sub_cat_size=size,sub_cat_gender=gender,sub_cat_homo=homo,sub_cat_melanoid = melanoid).paginate(
        page=page, per_page=row_per_page)

    if melanoid == "" and albino == "" and wild == "":
        print("leucistic is running")
        print(leucistic)
        product = Products.query.filter_by(sub_cat_size=size,sub_cat_gender=gender,sub_cat_homo=homo,sub_cat_leucistic = leucistic).paginate(
        page=page, per_page=row_per_page)



    print("size =",size,",","gender=",gender,",","homo=",homo,",","albino=",albino,",","melanoid=",melanoid,",","leucistic=",leucistic,",","wild=",wild,",","heter=",heter,",")
    try:
        cart_data = session["SHOP"]
    except:
        cart_data = {}


    plushies = Products.query.filter_by(category="Plushies").all()
    Handmade = Products.query.filter_by(category="Handmade").all()
    Swag = Products.query.filter_by(category="Swag").all()
    Axolotls = Products.query.filter_by(category = "Axolotls").all()
    return render_template(
        "shop.html",
        product=product,
        cart_data=cart_data,
        plushies=plushies,
        handmade=Handmade,
        swag=Swag,
        axolotls = Axolotls,
        cat='Axolotls',
    )

@app.route("/pro_cat/<cat>")
def pro_cat(cat):
    try:
        cart_data = session["SHOP"]
    except:
        cart_data = {}
    row_per_page = 10
    page = request.args.get("page", 1, type=int)
    product = Products.query.filter_by(category=cat).paginate(
        page=page, per_page=row_per_page
    )
    plushies = Products.query.filter_by(category="Plushies").all()
    Handmade = Products.query.filter_by(category="Handmade").all()
    Swag = Products.query.filter_by(category="Swag").all()
    Axolotls = Products.query.filter_by(category = "Axolotls").all()
    return render_template(
        "shop.html",
        product=product,
        cart_data=cart_data,
        plushies=plushies,
        handmade=Handmade,
        swag=Swag,
        axolotls = Axolotls,
        cat=cat,
    )


@app.route("/sub_cat/<cat>/<sub_cat>")
def sub_cat(cat, sub_cat):
    try:
        cart_data = session["SHOP"]
    except:
        cart_data = {}
    row_per_page = 10
    page = request.args.get("page", 1, type=int)
    product = Products.query.filter_by(category=cat, sub_category=sub_cat).paginate(
        page=page, per_page=row_per_page
    )
    plushies = Products.query.filter_by(category="Plushies").all()
    Handmade = Products.query.filter_by(category="Handmade").all()
    Swag = Products.query.filter_by(category="Swag").all()
    Axolotls = Products.query.filter_by(category = "Axolotls").all()

    return render_template(
        "shop.html",
        product=product,
        cart_data=cart_data,
        plushies=plushies,
        handmade=Handmade,
        swag=Swag,
        axolotls = Axolotls,
        cat=cat,
        sub_cat=sub_cat,
    )


@app.route("/details/<id>")
def product_details(id):
    # row_per_page = 10
    # page = request.args.get('page', 1, type=int)
    # rating = Ratings.query.filter_by(product_id=id).paginate(page = page , per_page = row_per_page)
    product = Products.query.filter_by(id=id).first()
    # user = User.query.all()
    return render_template("shop-details.html", product=product)


@app.route("/show_cart")
def show_cart():
    try:
        cart_data = session["SHOP"]
    except:
        cart_data = {}
    total_price = 0
    for key in cart_data:
        total_price = cart_data[key]["t_price"]

    print(cart_data)
    return render_template(
        "shopping-cart.html", cart_data=cart_data, total_price=total_price
    )


@app.route("/cart", methods=["GET", "POST"])
def add_to_cart():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        product = Products.query.filter_by(id=product_id).first()

        DictItems = {
            product_id: {
                "name": product.name,
                "price": product.unit_price,
                "t_price": product.unit_price,
                "description": product.description,
                "image": product.image,
                "quantity": 1,
            }
        }
        if "SHOP" in session:
            if product_id in session["SHOP"]:
                print("item id alreadys exists")
            else:
                session["SHOP"] = MergeDict(session["SHOP"], DictItems)
        else:
            session["SHOP"] = DictItems

        if "SHOP" in session:
            print(session["SHOP"])

        data = session["SHOP"]

        datas = len(data)
        return {"value": datas}


@app.route("/cart+", methods=["POST", "GET"])
def cart():
    if request.method == "POST":
        car_val = int(request.form.get("item_value"))
        price = float(request.form.get("price"))
        id = request.form.get("product_id")
        prod_price = float(request.form.get("prod_price"))
        product = Products.query.filter_by(id=id).first()
        if car_val >= product.stock:
            if "SHOP" in session:
                session["SHOP"][id]["quantity"] = car_val
                # session['SHOP'][id]['price'] = prod_price
                session["SHOP"][id]["t_price"] = prod_price
                session.modified = True
            return {
                "val": car_val,
                "total_price": prod_price,
                "prod_p": prod_price,
                "grand_total": price + 5,
            }

        car_val += 1
        price += product.unit_price
        print("___________________________________________")
        print(price)
        prod_price += product.unit_price
        if "SHOP" in session:
            session["SHOP"][id]["quantity"] = car_val
            # session['SHOP'][id]['price'] = prod_price
            session["SHOP"][id]["t_price"] = prod_price
            price = session["SHOP"][id]["t_price"]
            session.modified = True

        return {
            "val": car_val,
            "total_price": price,
            "prod_p": prod_price,
            "grand_total": price + 5,
        }


@app.route("/cart-", methods=["GET", "POST"])
def car_minus():
    if request.method == "POST":
        car_val = int(request.form.get("item_value"))
        price = float(request.form.get("price"))
        id = request.form.get("product_id")
        prod_price = float(request.form.get("prod_price"))

        product = Products.query.filter_by(id=id).first()
        car_val -= 1
        if car_val == 0:
            if "SHOP" in session:
                session["SHOP"][id]["quantity"] = 1
                session["SHOP"][id]["price"] = prod_price
                session.modified = True
            return {
                "val": 1,
                "total_price": price,
                "prod_p": prod_price,
                "grand_total": price + 5,
            }
        price -= product.unit_price
        prod_price -= product.unit_price
        if "SHOP" in session:
            session["SHOP"][id]["quantity"] = car_val
            session["SHOP"][id]["t_price"] = prod_price
            price = session["SHOP"][id]["t_price"]
            session.modified = True

        return {
            "val": car_val,
            "total_price": float(price),
            "prod_p": prod_price,
            "grand_total": price + 5,
        }


@app.route("/cart_item_delete/<key>")
def delete_session_item(key):
    if "SHOP" in session:
        session["SHOP"].pop(key)
        session.modified = True
    return redirect("/show_cart")


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    try:
        product = session["SHOP"]
    except:
        product = {}
    total_price = 0
    for key in product:
        total_price += product[key]["price"]

    if request.method == "POST":
        total_price = 0
        if "SHOP" in session:
            for key in session["SHOP"]:
                total_price += session["SHOP"][key]["price"]
        # cash, paymentMethod,zip,state,country, address2, address, email, name
        name = request.form["first_name"]
        email = request.form["email"]
        address = request.form["address"]
        address2 = request.form["address2"]
        country = request.form["country"]
        state = request.form["state"]
        zip = request.form["zip"]

        complete_address = (
            address + " " + address2 + " " + country + " " + state + " " + zip
        )
        data = Orders(
            user_id=current_user.id, total_price=total_price, address=complete_address
        )
        db.session.add(data)
        db.session.commit()
        db.session.refresh(data)

        # DictItems = {product_id:{"name":product.name, "price":product.unit_price, "description":product.description, "image":product.image, "quantity":1}}
        # if 'SHOP' in session:
        #     product = session['SHOP']
        for value in product:
            Items = OrderItems(
                order_id=data.id,
                product_id=value,
                quantity=product[value]["quantity"],
                unit_price=product[value]["price"],
            )
            db.session.add(Items)
            db.session.commit()

        for value in product:
            print()
            P_data = Products.query.filter_by(id=value).first()
            P_data.stock -= product[value]["quantity"]
            db.session.commit()

        session.pop("SHOP", None)
        session.modified = True
        return redirect("/confirmation/" + str(data.id))
    return render_template("checkout.html", product=product, total_price=total_price)


@app.route("/confirmation/<id>")
@login_required
def confirmation(id):
    try:
        print(session["SHOP"])
    except Exception as e:
        print(e)
    order = (
        db.session.query(OrderItems, Products)
        .join(Products, OrderItems.product_id == Products.id, isouter=True)
        .filter(OrderItems.order_id == id)
        .all()
    )
    print(type(order))
    total_price = 0
    for r in order:
        print(r[1].name, r[0].quantity, r[0].unit_price, r[1].image)
        total_price += r[0].unit_price
    data = Orders.query.filter_by(id=id).first()
    return render_template(
        "order_confirmation.html", order=order, data=data, total_price=total_price
    )


@app.route("/about")
def about():
    return render_template("")


@app.route("/update/<id>", methods=["POST", "GET"])
@login_required
def update(id):
    if current_user.name != "Admin" or current_user.email != "admin@gmail.com":
        flash("Please login as a admin to Access this page")
        return redirect("/login")
    update = "yes"
    product = Products.query.filter_by(id=id).first()
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        category = request.form.get("category")
        sub_category = request.form.get("sub-category")
        stock = request.form.get("stock")
        unit_price = request.form.get("unit_price")
        visibility = request.form.get("visibility")
        tag = request.form.get("tags")
        additional_desc = request.form.get("additional_description")
        file = request.files["image"]
        print(file.filename)
        if file.filename == "":
            filename = product.image
        else:
            filename = secure_filename(file.filename)
            print(filename.split(".")[1])
            if str(filename.split(".")[1]) not in Allowed:
                pass
                # flash("Our website does not support that type of extension, Please update your Product Image")
            file.save(os.path.join(Upload_dir, filename))

        if visibility.lower() == "true":
            visibility = 1
        else:
            visibility = 0
        product.name = name
        product.description = description
        product.category = category
        product.stock = stock
        product.unit_price = unit_price
        product.visibility = visibility
        product.tags = tag
        product.additional_description = additional_desc
        product.image = filename
        db.session.commit()
        return redirect("/admin_dashboard")
    return render_template(
        "/dashboard/pages/tables.html", update=update, product=product, cat="Update"
    )


@app.route("/history")
@login_required
def history():
    if current_user.name != "Admin" or current_user.email != "admin@gmail.com":
        flash("Please login as a admin to Access this page")
        return redirect("/login")
    row_per_page = 10
    page = request.args.get("page", 1, type=int)
    order = Orders.query.order_by(Orders.created.desc()).paginate(
        page=page, per_page=row_per_page
    )
    return render_template(
        "dashboard/pages/orders_history.html", order=order, cat="history"
    )


@app.route("/search", methods=["GET", "POST"])
def Search():
    row_per_page = 10
    page = request.args.get("page", 1, type=int)
    result = request.form["search"]
    print(result)
    product = Products.query.filter(
        or_(Products.tags.contains(result), Products.name.contains(result))
    ).paginate(page=page, per_page=row_per_page)
    plushies = Products.query.filter_by(category="Plushies").all()
    Handmade = Products.query.filter_by(category="Handmade").all()
    Swag = Products.query.filter_by(category="Swag").all()
    return render_template(
        "shop.html",
        product=product,
        result=result,
        plushies=plushies,
        handmade=Handmade,
        swag=Swag,
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", category="contact")


@app.route("/blog")
def blog():
    return render_template("blog.html")


@app.route("/blog_details")
def blog_details():
    return render_template("details.html")


@app.route("/logout")
@login_required
def user_logout():
    logout_user()
    return redirect("/")


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
