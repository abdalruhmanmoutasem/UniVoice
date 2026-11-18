from pathlib import Path
from flask import Flask, render_template
from config import Config
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .auth.routes import auth_bp
    from .student.routes import student_bp
    from .admin.routes import admin_bp
    from .staff.routes import staff_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(staff_bp, url_prefix="/staff")

    @app.route("/")
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return render_template("home.html", dashboard_url="/admin/")
            if current_user.role == "staff":
                return render_template("home.html", dashboard_url="/staff/")
            return render_template("home.html", dashboard_url="/student/")
        return render_template("home.html", dashboard_url="/login")

    @app.errorhandler(413)
    def too_large(_error):
        return "Upload too large. Maximum request size is 8 MB.", 413

    with app.app_context():
        db.create_all()
        from .models import Department
        if not Department.query.first():
            db.session.add_all([
                Department(name="Academic Affairs"),
                Department(name="Student Affairs"),
                Department(name="IT and Laboratories"),
                Department(name="Facilities"),
            ])
            db.session.commit()

    return app
