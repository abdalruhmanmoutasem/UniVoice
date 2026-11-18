from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from email_validator import validate_email, EmailNotValidError
from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            flash("Enter a valid email address.", "error")
            return render_template("auth/register.html")
        if not name or len(password) < 8:
            flash("Enter your name and a password with at least 8 characters.", "error")
            return render_template("auth/register.html")
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return render_template("auth/register.html")
        user = User(full_name=name, email=email, role="student")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("student.dashboard"))
    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            if user.role == "staff":
                return redirect(url_for("staff.dashboard"))
            return redirect(url_for("student.dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
