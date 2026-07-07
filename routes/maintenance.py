from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from models import db, MaintenanceLog, Asset, Vendor, AssetAssignment
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/', methods=['GET', 'POST'])
@login_required()
def list_logs():
    if request.method == 'POST':
        asset_id = request.form.get('asset_id')
        vendor_id = request.form.get('vendor_id')
        remarks = request.form.get('remarks')
        
        next_maint_date_str = request.form.get('next_maintenance_date')
        next_maintenance_date = datetime.strptime(next_maint_date_str, '%Y-%m-%d').date() if next_maint_date_str else None
        
        if not asset_id:
            flash('Please select an asset to log maintenance.', 'danger')
            return redirect(url_for('maintenance.list_logs'))
            
        asset = Asset.query.get(int(asset_id))
        if not asset:
            flash('Selected asset not found.', 'danger')
            return redirect(url_for('maintenance.list_logs'))
            
        # Initialize maintenance log
        log = MaintenanceLog(
            asset_id=asset.id,
            vendor_id=int(vendor_id) if vendor_id else None,
            remarks=remarks,
            next_maintenance_date=next_maintenance_date,
            status='Requested'
        )
        
        # Terminate any active assignment since it's going to maintenance
        if asset.status == 'Assigned' and asset.assigned_employee_id:
            active_ass = AssetAssignment.query.filter_by(asset_id=asset.id, returned_date=None).first()
            if active_ass:
                active_ass.returned_date = datetime.utcnow()
                active_ass.notes = f"{active_ass.notes or ''} [Checked in due to Maintenance request]."
            asset.assigned_employee_id = None
            
        # Update asset status
        asset.status = 'Maintenance'
        
        db.session.add(log)
        db.session.commit()
        
        flash(f"Maintenance request logged for asset '{asset.name}' ({asset.asset_id}).", 'success')
        return redirect(url_for('maintenance.list_logs'))
        
    logs = MaintenanceLog.query.order_by(MaintenanceLog.request_date.desc()).all()
    # Assets available for maintenance (not Retired)
    assets = Asset.query.filter(Asset.status != 'Retired').order_by(Asset.asset_id).all()
    vendors = Vendor.query.all()
    
    return render_template(
        'maintenance/list.html',
        logs=logs,
        assets=assets,
        vendors=vendors
    )

@maintenance_bp.route('/<int:id>/complete', methods=['POST'])
@login_required()
def complete_log(id):
    log = MaintenanceLog.query.get_or_404(id)
    
    cost_str = request.form.get('cost')
    cost = float(cost_str) if cost_str else 0.0
    
    remarks = request.form.get('remarks')
    
    next_maint_date_str = request.form.get('next_maintenance_date')
    next_maintenance_date = datetime.strptime(next_maint_date_str, '%Y-%m-%d').date() if next_maint_date_str else None
    
    log.status = 'Completed'
    log.cost = cost
    log.service_date = datetime.utcnow()
    log.remarks = f"{log.remarks or ''} | Completion Notes: {remarks or 'None'}"
    if next_maintenance_date:
        log.next_maintenance_date = next_maintenance_date
        
    # Reset asset status to Available
    asset = Asset.query.get(log.asset_id)
    if asset:
        asset.status = 'Available'
        
    db.session.commit()
    flash(f"Maintenance completed for asset '{asset.name}'. Cost: ${cost:.2f}", 'success')
    return redirect(url_for('maintenance.list_logs'))

@maintenance_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required()
def cancel_log(id):
    log = MaintenanceLog.query.get_or_404(id)
    log.status = 'Cancelled'
    
    # Restore asset to Available
    asset = Asset.query.get(log.asset_id)
    if asset:
        asset.status = 'Available'
        
    db.session.commit()
    flash(f"Maintenance request for asset '{asset.name}' has been cancelled.", 'success')
    return redirect(url_for('maintenance.list_logs'))
