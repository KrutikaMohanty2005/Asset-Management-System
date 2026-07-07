from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from routes.auth import login_required
from models import db, Asset, Category, Location, Vendor, Employee, AssetAssignment, MaintenanceLog
from datetime import datetime
import os
from werkzeug.utils import secure_filename

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def handle_file_upload(file_field_name, subfolder):
    if file_field_name not in request.files:
        return None
    file = request.files[file_field_name]
    if file.filename == '':
        return None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure timestamp prefix to avoid overrides
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + filename
        
        # Ensure upload folder path exists
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        file.save(os.path.join(upload_path, filename))
        return f"uploads/{subfolder}/{filename}"
    return None

@assets_bp.route('/')
@login_required()
def list_assets():
    # Filters
    q = request.args.get('q', '').strip()
    cat_id = request.args.get('category', '')
    loc_id = request.args.get('location', '')
    status = request.args.get('status', '')
    
    query = Asset.query
    
    if q:
        query = query.filter(
            (Asset.name.like(f"%{q}%")) | 
            (Asset.asset_id.like(f"%{q}%")) | 
            (Asset.serial_number.like(f"%{q}%")) |
            (Asset.brand_model.like(f"%{q}%"))
        )
        
    if cat_id:
        query = query.filter(Asset.category_id == int(cat_id))
        
    if loc_id:
        query = query.filter(Asset.location_id == int(loc_id))
        
    if status:
        query = query.filter(Asset.status == status)
        
    assets = query.order_by(Asset.created_at.desc()).all()
    
    categories = Category.query.all()
    locations = Location.query.all()
    
    return render_template(
        'assets/list.html',
        assets=assets,
        categories=categories,
        locations=locations,
        q=q,
        cat_id=cat_id,
        loc_id=loc_id,
        status=status
    )

@assets_bp.route('/<int:id>')
@login_required()
def asset_details(id):
    asset = Asset.query.get_or_404(id)
    
    # Assignments history
    assignments = AssetAssignment.query.filter_by(asset_id=id).order_by(AssetAssignment.assigned_date.desc()).all()
    
    # Maintenance logs
    maintenance = MaintenanceLog.query.filter_by(asset_id=id).order_by(MaintenanceLog.request_date.desc()).all()
    
    # Timeline compiler
    timeline = []
    for ass in assignments:
        timeline.append({
            'date': ass.assigned_date,
            'title': 'Asset Assigned',
            'detail': f"Assigned to {ass.employee.name} (ID: {ass.employee.employee_id}) by {ass.assigner.username}.",
            'icon': 'fa-user-tag',
            'class': 'text-primary'
        })
        if ass.returned_date:
            timeline.append({
                'date': ass.returned_date,
                'title': 'Asset Returned',
                'detail': f"Returned by {ass.employee.name}. Checked in back to system.",
                'icon': 'fa-circle-check',
                'class': 'text-success'
            })
            
    for log in maintenance:
        timeline.append({
            'date': log.request_date,
            'title': 'Maintenance Log Initiated',
            'detail': f"Requested maintenance service. Status: {log.status}. Details: {log.remarks or 'None'}",
            'icon': 'fa-screwdriver-wrench',
            'class': 'text-warning'
        })
        if log.service_date:
            timeline.append({
                'date': log.service_date,
                'title': 'Maintenance Completed',
                'detail': f"Service completed by vendor. Total Cost: ${log.cost or '0.00'}. Status updated to {log.status}.",
                'icon': 'fa-check-double',
                'class': 'text-info'
            })
            
    # Sort timeline by date descending
    timeline = sorted(timeline, key=lambda x: x['date'], reverse=True)
    
    return render_template(
        'assets/details.html',
        asset=asset,
        assignments=assignments,
        maintenance=maintenance,
        timeline=timeline,
        datetime_today=datetime.utcnow().date()
    )

@assets_bp.route('/new', methods=['GET', 'POST'])
@login_required()
def add_asset():
    if request.method == 'POST':
        asset_id = request.form.get('asset_id')
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        brand_model = request.form.get('brand_model')
        serial_number = request.form.get('serial_number')
        
        purchase_date_str = request.form.get('purchase_date')
        purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date() if purchase_date_str else None
        
        purchase_cost = request.form.get('purchase_cost')
        purchase_cost = float(purchase_cost) if purchase_cost else None
        
        warranty_expiry_str = request.form.get('warranty_expiry')
        warranty_expiry = datetime.strptime(warranty_expiry_str, '%Y-%m-%d').date() if warranty_expiry_str else None
        
        vendor_id = request.form.get('vendor_id')
        vendor_id = int(vendor_id) if vendor_id else None
        
        location_id = request.form.get('location_id')
        assigned_employee_id = request.form.get('assigned_employee_id')
        assigned_employee_id = int(assigned_employee_id) if assigned_employee_id else None
        
        status = request.form.get('status', 'Available')
        
        # Basic validation
        if not asset_id or not name or not category_id or not location_id:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('assets.add_asset'))
            
        if Asset.query.filter_by(asset_id=asset_id).first():
            flash(f"Asset ID '{asset_id}' already exists.", 'danger')
            return redirect(url_for('assets.add_asset'))
            
        # File uploads
        invoice_path = handle_file_upload('invoice', 'invoices')
        image_path = handle_file_upload('image', 'images')
        
        # QR Code URL generation (API based)
        qr_code_path = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={asset_id}"
        
        asset = Asset(
            asset_id=asset_id,
            name=name,
            category_id=int(category_id),
            brand_model=brand_model,
            serial_number=serial_number,
            purchase_date=purchase_date,
            purchase_cost=purchase_cost,
            warranty_expiry=warranty_expiry,
            vendor_id=vendor_id,
            location_id=int(location_id),
            status=status,
            invoice_path=invoice_path,
            image_path=image_path,
            qr_code_path=qr_code_path
        )
        
        # Handle assignment if assigned right away
        if status == 'Assigned':
            if not assigned_employee_id:
                flash('Please select an employee to assign this asset.', 'danger')
                return redirect(url_for('assets.add_asset'))
            asset.assigned_employee_id = assigned_employee_id
            
        db.session.add(asset)
        db.session.commit()
        
        # Record assignment log if status was set to Assigned
        if status == 'Assigned' and assigned_employee_id:
            assignment = AssetAssignment(
                asset_id=asset.id,
                employee_id=assigned_employee_id,
                assigned_by=session['user_id'],
                notes="Initial assignment during asset creation."
            )
            db.session.add(assignment)
            db.session.commit()
            
        flash(f"Asset '{name}' created successfully.", 'success')
        return redirect(url_for('assets.list_assets'))
        
    categories = Category.query.all()
    locations = Location.query.all()
    vendors = Vendor.query.all()
    employees = Employee.query.filter_by(status='Active').all()
    
    # Auto-generate mock Asset ID
    next_num = Asset.query.count() + 1
    suggested_id = f"AST-{next_num:04d}"
    
    return render_template(
        'assets/add_edit.html',
        asset=None,
        categories=categories,
        locations=locations,
        vendors=vendors,
        employees=employees,
        suggested_id=suggested_id
    )

@assets_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required()
def edit_asset(id):
    asset = Asset.query.get_or_404(id)
    old_status = asset.status
    old_employee_id = asset.assigned_employee_id
    
    if request.method == 'POST':
        asset.name = request.form.get('name')
        asset.category_id = int(request.form.get('category_id'))
        asset.brand_model = request.form.get('brand_model')
        asset.serial_number = request.form.get('serial_number')
        
        purchase_date_str = request.form.get('purchase_date')
        asset.purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date() if purchase_date_str else None
        
        purchase_cost = request.form.get('purchase_cost')
        asset.purchase_cost = float(purchase_cost) if purchase_cost else None
        
        warranty_expiry_str = request.form.get('warranty_expiry')
        asset.warranty_expiry = datetime.strptime(warranty_expiry_str, '%Y-%m-%d').date() if warranty_expiry_str else None
        
        vendor_id = request.form.get('vendor_id')
        asset.vendor_id = int(vendor_id) if vendor_id else None
        
        asset.location_id = int(request.form.get('location_id'))
        
        new_status = request.form.get('status')
        new_employee_id = request.form.get('assigned_employee_id')
        new_employee_id = int(new_employee_id) if new_employee_id else None
        
        # File uploads (updates old paths if new files are selected)
        new_invoice = handle_file_upload('invoice', 'invoices')
        if new_invoice:
            asset.invoice_path = new_invoice
            
        new_image = handle_file_upload('image', 'images')
        if new_image:
            asset.image_path = new_image
            
        # Manage Assignments Logs based on Status changes
        if new_status == 'Assigned':
            if not new_employee_id:
                flash('Please select an employee to assign this asset.', 'danger')
                return redirect(url_for('assets.edit_asset', id=id))
            
            # If status changed to Assigned, or Employee changed
            if old_status != 'Assigned' or old_employee_id != new_employee_id:
                # Terminate active previous assignment if there was one (unlikely but safe)
                active_ass = AssetAssignment.query.filter_by(asset_id=id, returned_date=None).first()
                if active_ass:
                    active_ass.returned_date = datetime.utcnow()
                
                # Assign to new employee
                asset.assigned_employee_id = new_employee_id
                assignment = AssetAssignment(
                    asset_id=id,
                    employee_id=new_employee_id,
                    assigned_by=session['user_id'],
                    notes=request.form.get('notes', 'Asset status updated via edit.')
                )
                db.session.add(assignment)
                
        elif new_status == 'Available':
            # Check in the asset
            asset.assigned_employee_id = None
            active_ass = AssetAssignment.query.filter_by(asset_id=id, returned_date=None).first()
            if active_ass:
                active_ass.returned_date = datetime.utcnow()
                
        else: # Maintenance or Retired
            # Check in the asset
            asset.assigned_employee_id = None
            active_ass = AssetAssignment.query.filter_by(asset_id=id, returned_date=None).first()
            if active_ass:
                active_ass.returned_date = datetime.utcnow()
                
        asset.status = new_status
        db.session.commit()
        
        flash(f"Asset '{asset.name}' updated successfully.", 'success')
        return redirect(url_for('assets.list_assets'))
        
    categories = Category.query.all()
    locations = Location.query.all()
    vendors = Vendor.query.all()
    employees = Employee.query.filter_by(status='Active').all()
    
    return render_template(
        'assets/add_edit.html',
        asset=asset,
        categories=categories,
        locations=locations,
        vendors=vendors,
        employees=employees,
        suggested_id=None
    )

@assets_bp.route('/<int:id>/delete', methods=['POST'])
@login_required(role=['admin', 'manager'])
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    name = asset.name
    
    db.session.delete(asset)
    db.session.commit()
    
    flash(f"Asset '{name}' deleted successfully.", 'success')
    return redirect(url_for('assets.list_assets'))
