from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, Vendor, Asset

vendors_bp = Blueprint('vendors', __name__, url_prefix='/vendors')

@vendors_bp.route('/', methods=['GET', 'POST'])
@login_required()
def list_vendors():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        if not name:
            flash('Vendor name is required.', 'danger')
            return redirect(url_for('vendors.list_vendors'))
            
        vendor = Vendor(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address
        )
        db.session.add(vendor)
        db.session.commit()
        
        flash(f"Vendor '{name}' created successfully.", 'success')
        return redirect(url_for('vendors.list_vendors'))
        
    vendors = Vendor.query.all()
    return render_template('vendors/list.html', vendors=vendors)

@vendors_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required(role=['admin', 'manager'])
def edit_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        if not name:
            flash('Vendor name is required.', 'danger')
            return redirect(url_for('vendors.edit_vendor', id=id))
            
        vendor.name = name
        vendor.contact_person = contact_person
        vendor.email = email
        vendor.phone = phone
        vendor.address = address
        db.session.commit()
        
        flash(f"Vendor '{name}' updated successfully.", 'success')
        return redirect(url_for('vendors.list_vendors'))
        
    return render_template('vendors/list.html', vendors=Vendor.query.all(), edit_vendor=vendor)

@vendors_bp.route('/<int:id>/delete', methods=['POST'])
@login_required(role=['admin', 'manager'])
def delete_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    
    asset_count = Asset.query.filter_by(vendor_id=id).count()
    if asset_count > 0:
        flash(f"Cannot delete vendor '{vendor.name}' because it has {asset_count} associated asset(s).", 'danger')
        return redirect(url_for('vendors.list_vendors'))
        
    name = vendor.name
    db.session.delete(vendor)
    db.session.commit()
    
    flash(f"Vendor '{name}' deleted successfully.", 'success')
    return redirect(url_for('vendors.list_vendors'))
