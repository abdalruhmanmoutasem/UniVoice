from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

def utcnow():
    return datetime.now(timezone.utc)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    department = db.relationship("Department")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    request_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    student = db.relationship("User", foreign_keys=[student_id])
    assigned_staff = db.relationship("User", foreign_keys=[assigned_staff_id])
    department = db.relationship("Department")
    attachments = db.relationship("Attachment", backref="request", cascade="all, delete-orphan")
    replies = db.relationship("Reply", backref="request", cascade="all, delete-orphan", order_by="Reply.created_at")
    history = db.relationship("StatusHistory", backref="request", cascade="all, delete-orphan", order_by="StatusHistory.changed_at")

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    author = db.relationship("User")

class StatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    changed_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    actor = db.relationship("User")

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
