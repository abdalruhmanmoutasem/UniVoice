from pathlib import Path
from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Request as StudentRequest, Attachment, Department, Feedback

student_bp = Blueprint("student", __name__)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024

def student_only():
    if current_user.role != "student":
        abort(403)

@student_bp.route("/")
@login_required
def dashboard():
    student_only()
    requests = StudentRequest.query.filter_by(student_id=current_user.id).order_by(StudentRequest.created_at.desc()).all()
    return render_template("student/dashboard.html", requests=requests)

@student_bp.route("/requests/new", methods=["GET", "POST"])
@login_required
def new_request():
    student_only()
    departments = Department.query.order_by(Department.name).all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        kind = request.form.get("request_type", "")
        category = request.form.get("category", "").strip()
        if not title or not description or kind not in {"Complaint", "Suggestion"} or not category:
            flash("Complete all required fields.", "error")
            return render_template("student/new_request.html", departments=departments)
        item = StudentRequest(
            ticket_code=f"UV-{__import__('datetime').datetime.now().year}-{uuid4().hex[:8].upper()}",
            student_id=current_user.id, title=title, description=description,
            request_type=kind, category=category, status="Pending"
        )
        db.session.add(item)
        db.session.flush()
        files = request.files.getlist("attachments")
        upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
        for uploaded in files:
            if not uploaded or not uploaded.filename:
                continue
            original = secure_filename(uploaded.filename)
            ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
            if ext not in ALLOWED_EXTENSIONS:
                db.session.rollback()
                flash("Only PNG, JPG, JPEG, WEBP and PDF files are allowed.", "error")
                return render_template("student/new_request.html", departments=departments)
            uploaded.stream.seek(0, 2)
            size = uploaded.stream.tell()
            uploaded.stream.seek(0)
            if size > MAX_FILE_SIZE:
                db.session.rollback()
                flash("Each attachment must be 5 MB or smaller.", "error")
                return render_template("student/new_request.html", departments=departments)
            stored = f"{uuid4().hex}.{ext}"
            uploaded.save(upload_dir / stored)
            db.session.add(Attachment(request_id=item.id, stored_name=stored, original_name=original))
        db.session.commit()
        flash(f"Request submitted. Your tracking code is {item.ticket_code}.", "success")
        return redirect(url_for("student.dashboard"))
    return render_template("student/new_request.html", departments=departments)

@student_bp.route("/requests/<int:request_id>")
@login_required
def request_detail(request_id):
    student_only()
    item = StudentRequest.query.filter_by(id=request_id, student_id=current_user.id).first_or_404()
    return render_template("student/request_detail.html", item=item)

@student_bp.route("/requests/<int:request_id>/feedback", methods=["POST"])
@login_required
def feedback(request_id):
    student_only()
    item = StudentRequest.query.filter_by(id=request_id, student_id=current_user.id, status="Resolved").first_or_404()
    if Feedback.query.filter_by(request_id=item.id).first():
        flash("Feedback has already been submitted.", "error")
    else:
        try:
            rating = int(request.form.get("rating", ""))
        except ValueError:
            rating = 0
        if rating not in range(1, 6):
            flash("Choose a rating from 1 to 5.", "error")
        else:
            db.session.add(Feedback(request_id=item.id, student_id=current_user.id, rating=rating,
                                    comment=request.form.get("comment", "").strip()[:500]))
            db.session.commit()
            flash("Thank you for your feedback.", "success")
    return redirect(url_for("student.request_detail", request_id=item.id))
