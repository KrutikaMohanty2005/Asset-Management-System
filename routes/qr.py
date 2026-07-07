from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from routes.auth import login_required
from models import db, Asset, Employee, AssetAssignment, MaintenanceLog
from datetime import datetime

qr_bp = Blueprint('qr', __name__, url_prefix='/qr')

@qr_bp.route('/scan')
@login_required()
def scanner_view():
    return render_template('qr/scanner.html')

@qr_bp.route('/decode', methods=['POST'])
@login_required()
def decode_qr():
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({'success': False, 'message': 'No code payload received.'}), 400
        
    code_value = data['code'].strip()
    
    # Check if the code matches an existing asset ID
    asset = Asset.query.filter_by(asset_id=code_value).first()
    
    if asset:
        # Return the redirection URL for the Scan Result page
        redirect_url = url_for('qr.scan_result', asset_id=asset.asset_id)
        return jsonify({'success': True, 'redirect_url': redirect_url})
    else:
        return jsonify({'success': False, 'message': f"Asset ID '{code_value}' not found in registry."})

@qr_bp.route('/result')
@login_required()
def scan_result():
    asset_id = request.args.get('asset_id')
    if not asset_id:
        flash('No Asset ID provided for lookup.', 'danger')
        return redirect(url_for('qr.scanner_view'))
        
    asset = Asset.query.filter_by(asset_id=asset_id).first()
    if not asset:
        flash(f"Asset with ID '{asset_id}' not found.", 'danger')
        return redirect(url_for('qr.scanner_view'))
        
    employees = Employee.query.filter_by(status='Active').all()
    
    return render_template(
        'qr/result.html',
        asset=asset,
        employees=employees
    )

@qr_bp.route('/result/action', methods=['POST'])
@login_required()
def scan_result_action():
    asset_id = request.form.get('asset_id')
    action = request.form.get('action') # assign, return, maintenance
    
    asset = Asset.query.filter_by(asset_id=asset_id).first()
    if not asset:
        flash('Asset not found.', 'danger')
        return redirect(url_for('qr.scanner_view'))
        
    if action == 'return':
        asset.status = 'Available'
        asset.assigned_employee_id = None
        active_ass = AssetAssignment.query.filter_by(asset_id=asset.id, returned_date=None).first()
        if active_ass:
            active_ass.returned_date = datetime.utcnow()
            active_ass.notes = f"{active_ass.notes or ''} [Checked in via QR Scan Quick Action]."
        db.session.commit()
        flash(f"Asset '{asset.name}' has been checked back in.", 'success')
        
    elif action == 'assign':
        employee_id = request.form.get('assigned_employee_id')
        if not employee_id:
            flash('Please select an employee to assign this asset.', 'danger')
            return redirect(url_for('qr.scan_result', asset_id=asset_id))
            
        employee = Employee.query.get(int(employee_id))
        if not employee:
            flash('Employee not found.', 'danger')
            return redirect(url_for('qr.scan_result', asset_id=asset_id))
            
        # Terminate any active assignment first
        active_ass = AssetAssignment.query.filter_by(asset_id=asset.id, returned_date=None).first()
        if active_ass:
            active_ass.returned_date = datetime.utcnow()
            
        asset.status = 'Assigned'
        asset.assigned_employee_id = employee.id
        
        assignment = AssetAssignment(
            asset_id=asset.id,
            employee_id=employee.id,
            assigned_by=session['user_id'],
            notes="Assigned via QR Scan Quick Action."
        )
        db.session.add(assignment)
        db.session.commit()
        flash(f"Asset '{asset.name}' assigned to {employee.name}.", 'success')
        
    elif action == 'maintenance':
        remarks = request.form.get('remarks', 'Initiated via QR Scan Quick Action.')
        
        # Terminate assignment
        if asset.status == 'Assigned':
            active_ass = AssetAssignment.query.filter_by(asset_id=asset.id, returned_date=None).first()
            if active_ass:
                active_ass.returned_date = datetime.utcnow()
            asset.assigned_employee_id = None
            
        asset.status = 'Maintenance'
        
        log = MaintenanceLog(
            asset_id=asset.id,
            remarks=remarks,
            status='Requested'
        )
        db.session.add(log)
        db.session.commit()
        flash(f"Asset '{asset.name}' sent to Maintenance logs.", 'success')
        
    return redirect(url_for('qr.scan_result', asset_id=asset_id))
