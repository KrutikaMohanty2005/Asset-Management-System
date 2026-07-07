from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, Employee, Asset

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employees_bp.route('/', methods=['GET', 'POST'])
@login_required()
def list_employees():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id').strip()
        name = request.form.get('name').strip()
        department = request.form.get('department').strip()
        designation = request.form.get('designation').strip()
        contact = request.form.get('contact').strip()
        email = request.form.get('email').strip()
        
        if not employee_id or not name or not email:
            flash('Employee ID, Name, and Email are required fields.', 'danger')
            return redirect(url_for('employees.list_employees'))
            
        # Uniqueness checks
        if Employee.query.filter_by(employee_id=employee_id).first():
            flash(f"Employee ID '{employee_id}' is already registered.", 'danger')
            return redirect(url_for('employees.list_employees'))
            
        if Employee.query.filter_by(email=email).first():
            flash(f"Email '{email}' is already in use.", 'danger')
            return redirect(url_for('employees.list_employees'))
            
        employee = Employee(
            employee_id=employee_id,
            name=name,
            department=department,
            designation=designation,
            contact=contact,
            email=email,
            status='Active'
        )
        
        db.session.add(employee)
        db.session.commit()
        
        flash(f"Employee '{name}' added successfully.", 'success')
        return redirect(url_for('employees.list_employees'))
        
    employees = Employee.query.order_by(Employee.created_at.desc()).all()
    
    # Auto-generate mock Employee ID
    next_num = Employee.query.count() + 1
    suggested_id = f"EMP-{next_num:03d}"
    
    return render_template(
        'employees/list.html',
        employees=employees,
        suggested_id=suggested_id,
        edit_employee=None
    )

@employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required()
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name').strip()
        department = request.form.get('department').strip()
        designation = request.form.get('designation').strip()
        contact = request.form.get('contact').strip()
        email = request.form.get('email').strip()
        status = request.form.get('status', 'Active')
        
        if not name or not email:
            flash('Name and Email are required fields.', 'danger')
            return redirect(url_for('employees.edit_employee', id=id))
            
        # Email uniqueness check (excluding self)
        existing_email = Employee.query.filter(Employee.email == email, Employee.id != id).first()
        if existing_email:
            flash(f"Email '{email}' is already in use by another employee.", 'danger')
            return redirect(url_for('employees.edit_employee', id=id))
            
        employee.name = name
        employee.department = department
        employee.designation = designation
        employee.contact = contact
        employee.email = email
        employee.status = status
        
        db.session.commit()
        flash(f"Employee '{name}' updated successfully.", 'success')
        return redirect(url_for('employees.list_employees'))
        
    employees = Employee.query.order_by(Employee.created_at.desc()).all()
    return render_template(
        'employees/list.html',
        employees=employees,
        suggested_id=None,
        edit_employee=employee
    )

@employees_bp.route('/<int:id>/delete', methods=['POST'])
@login_required(role=['admin', 'manager'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # Safety Check: check if employee has active assigned assets
    assigned_assets_count = Asset.query.filter_by(assigned_employee_id=id, status='Assigned').count()
    if assigned_assets_count > 0:
        flash(f"Cannot delete employee '{employee.name}' because they currently have {assigned_assets_count} assigned asset(s). Please return/check-in the assets first.", 'danger')
        return redirect(url_for('employees.list_employees'))
        
    name = employee.name
    db.session.delete(employee)
    db.session.commit()
    
    flash(f"Employee '{name}' deleted successfully.", 'success')
    return redirect(url_for('employees.list_employees'))
