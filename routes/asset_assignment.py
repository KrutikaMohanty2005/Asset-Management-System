from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from models import db, Asset, Employee, AssetAssignment
from datetime import datetime

asset_assignment_bp = Blueprint('asset_assignment', __name__, url_prefix='/asset-assignment')

@asset_assignment_bp.route('/', methods=['GET', 'POST'])
@login_required()
def list_assignments():
    if request.method == 'POST':
        asset_id = request.form.get('asset_id')
        employee_id = request.form.get('employee_id')
        notes = request.form.get('notes', '').strip()
        
        if not asset_id or not employee_id:
            flash('Please select both an asset and an employee.', 'danger')
            return redirect(url_for('asset_assignment.list_assignments'))
            
        asset = Asset.query.get(int(asset_id))
        employee = Employee.query.get(int(employee_id))
        
        if not asset or not employee:
            flash('Invalid asset or employee selected.', 'danger')
            return redirect(url_for('asset_assignment.list_assignments'))
            
        if asset.status != 'Available':
            flash(f"Asset '{asset.name}' is not available for assignment (Status: {asset.status}).", 'danger')
            return redirect(url_for('asset_assignment.list_assignments'))
            
        # Terminate any active assignment
        active_ass = AssetAssignment.query.filter_by(asset_id=asset.id, returned_date=None).first()
        if active_ass:
            active_ass.returned_date = datetime.utcnow()
            
        asset.status = 'Assigned'
        asset.assigned_employee_id = employee.id
        
        assignment = AssetAssignment(
            asset_id=asset.id,
            employee_id=employee.id,
            assigned_by=session['user_id'],
            notes=notes or 'Assigned via Asset Assignment page.'
        )
        db.session.add(assignment)
        db.session.commit()
        
        flash(f"Asset '{asset.name}' assigned to {employee.name} successfully.", 'success')
        return redirect(url_for('asset_assignment.list_assignments'))
        
    assignments = AssetAssignment.query.order_by(AssetAssignment.assigned_date.desc()).all()
    available_assets = Asset.query.filter_by(status='Available').all()
    active_employees = Employee.query.filter_by(status='Active').all()
    
    return render_template(
        'asset_assignment/list.html',
        assignments=assignments,
        available_assets=available_assets,
        active_employees=active_employees
    )
