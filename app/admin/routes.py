from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Request as StudentRequest, User, Department, StatusHistory

admin_bp = Blueprint("admin", __name__)
STATUSES = ["Pending", "Under Review", "In Progress", "Resolved", "Rejected"]

def admin_only():
    if current_user.role != "admin":
        abort(403)

@admin_bp.route("/")
@login_required
def dashboard():
    admin_only()
    requests = StudentRequest.query.order_by(StudentRequest.created_at.desc()).all()
    return render_template("admin/dashboard.html", requests=requests,
                           total=len(requests),
                           pending=sum(r.status == "Pending" for r in requests),
                           resolved=sum(r.status == "Resolved" for r in requests))

@admin_bp.route("/requests/<int:request_id>", methods=["GET", "POST"])
@login_required
def manage_request(request_id):
    admin_only()
    item = StudentRequest.query.get_or_404(request_id)
    staff = User.query.filter_by(role="staff").all()
    departments = Department.query.all()
    if request.method == "POST":
        old = item.status
        new_status = request.form.get("status", old)
        staff_id = request.form.get("assigned_staff_id") or None
        department_id = request.form.get("department_id") or None
        if new_status not in STATUSES:
            abort(400)
        if staff_id:
            selected_staff = User.query.filter_by(id=int(staff_id), role="staff").first()
            if not selected_staff:
                abort(400)
            if department_id and selected_staff.department_id != int(department_id):
                flash("The selected staff member must belong to the selected department.", "error")
                return render_template("admin/manage_request.html", item=item, staff=staff, departments=departments, statuses=STATUSES)
        item.status = new_status
        item.assigned_staff_id = int(staff_id) if staff_id else None
        item.department_id = int(department_id) if department_id else None
        if old != new_status:
            db.session.add(StatusHistory(request_id=item.id, changed_by=current_user.id, old_status=old, new_status=new_status))
        db.session.commit()
        flash("Request updated.", "success")
        return redirect(url_for("admin.manage_request", request_id=item.id))
    return render_template("admin/manage_request.html", item=item, staff=staff, departments=departments, statuses=STATUSES)

@admin_bp.route("/staff", methods=["GET", "POST"])
@login_required
def manage_staff():
    admin_only()
    departments = Department.query.all()
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        department_id = request.form.get("department_id")
        if not name or not email or len(password) < 8 or not department_id:
            flash("Complete all fields. Password must be at least 8 characters.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email already exists.", "error")
        else:
            user = User(full_name=name, email=email, role="staff", department_id=int(department_id))
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Staff account created.", "success")
    staff = User.query.filter_by(role="staff").all()
    return render_template("admin/staff.html", staff=staff, departments=departments)
