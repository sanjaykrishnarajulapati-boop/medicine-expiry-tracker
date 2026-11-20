
import os
from datetime import date, datetime

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)

from models import db, User, Medicine


app = Flask(__name__)

# Development fallback. Set a strong SECRET_KEY environment
# variable before deploying online.
secret_key = os.environ.get("SECRET_KEY")

if not secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required.")

app.config["SECRET_KEY"] = secret_key

# Database configuration
os.makedirs(app.instance_path, exist_ok=True)


# Database configuration
database_url = os.environ.get("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///medicine_tracker.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connect database
db.init_app(app)

# Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Create database tables
with app.app_context():
    db.create_all()


def get_status(expiry_date):
    days_left = (expiry_date - date.today()).days

    if days_left < 0:
        return "Expired", days_left
    elif days_left <= 30:
        return "Expiring soon", days_left
    else:
        return "Safe", days_left


@app.route("/")
@login_required
def home():
    medicines = Medicine.query.filter_by(
        user_id=current_user.id
    ).all()

    expired = 0
    expiring_soon = 0
    safe = 0

    for medicine in medicines:
        status, days_left = get_status(medicine.expiry_date)

        medicine.status = status
        medicine.days_left = days_left

        if status == "Expired":
            expired += 1
        elif status == "Expiring soon":
            expiring_soon += 1
        else:
            safe += 1

    medicines.sort(key=lambda item: item.expiry_date)

    dashboard = {
        "total": len(medicines),
        "expired": expired,
        "expiring_soon": expiring_soon,
        "safe": safe
    }

    return render_template(
        "index.html",
        medicines=medicines,
        dashboard=dashboard,
        today=date.today()
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter a username and password.", "error")
            return redirect(url_for("register"))

        if len(username) > 80:
            flash("Username must be 80 characters or fewer.", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("That username is already registered.", "error")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        flash("Account created successfully.", "success")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(
            user.password_hash, password
        ):
            login_user(user)
            flash("Login successful.", "success")
            return redirect(url_for("home"))

        flash("Incorrect username or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "success")
    return redirect(url_for("login"))


@app.route("/add", methods=["POST"])
@login_required
def add_medicine():
    name = request.form.get("name", "").strip()
    quantity = request.form.get("quantity", "").strip()
    expiry_text = request.form.get("expiry_date", "").strip()
    notes = request.form.get("notes", "").strip()

    if not name or not quantity or not expiry_text:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("home"))

    if len(name) > 80 or len(notes) > 160:
        flash("Medicine name or notes are too long.", "error")
        return redirect(url_for("home"))

    try:
        quantity_number = int(quantity)
        parsed_date = datetime.strptime(
            expiry_text, "%Y-%m-%d"
        ).date()

        if quantity_number <= 0:
            raise ValueError

    except ValueError:
        flash("Enter a valid quantity and expiry date.", "error")
        return redirect(url_for("home"))

    medicine = Medicine(
        name=name,
        quantity=quantity_number,
        expiry_date=parsed_date,
        notes=notes,
        user_id=current_user.id
    )

    db.session.add(medicine)
    db.session.commit()

    flash("Medicine added successfully.", "success")
    return redirect(url_for("home"))


@app.route("/delete/<int:medicine_id>", methods=["POST"])
@login_required
def delete_medicine(medicine_id):
    medicine = Medicine.query.filter_by(
        id=medicine_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(medicine)
    db.session.commit()

    flash("Medicine record deleted.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
