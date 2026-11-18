from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Request as StudentRequest, Reply, StatusHistory

staff_bp = Blueprint("staff", __name__)
STATUSES = ["Under Review", "In Progress", "Resolved"]

def staff_only():
    if current_user.role != "staff":
        abort(403)

@staff_bp.route("/")
@login_required
def dashboard():
    staff_only()
    requests = StudentRequest.query.filter_by(assigned_staff_id=current_user.id).order_by(StudentRequest.created_at.desc()).all()
    return render_template("staff/dashboard.html", requests=requests)

@staff_bp.route("/requests/<int:request_id>", methods=["GET", "POST"])
@login_required
def request_detail(request_id):
    staff_only()
    item = StudentRequest.query.filter_by(id=request_id, assigned_staff_id=current_user.id).first_or_404()
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        new_status = request.form.get("status", item.status)
        if new_status not in STATUSES:
            abort(400)
        if message:
            db.session.add(Reply(request_id=item.id, user_id=current_user.id, message=message))
        old = item.status
        item.status = new_status
        if old != new_status:
            db.session.add(StatusHistory(request_id=item.id, changed_by=current_user.id, old_status=old, new_status=new_status))
        db.session.commit()
        flash("Request updated.", "success")
        return redirect(url_for("staff.request_detail", request_id=item.id))
    return render_template("staff/request_detail.html", item=item, statuses=STATUSES)
