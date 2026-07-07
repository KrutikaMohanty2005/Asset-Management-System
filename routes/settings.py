from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from models import db, Settings, Category, Location, Vendor

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required(role=['admin', 'manager'])
def settings_view():
    if request.method == 'POST':
        # List of expected settings fields
        fields = [
            'company_name', 'currency', 'timezone', 
            'email_sender', 'email_smtp_server', 'email_smtp_port',
            'backup_frequency', 'backup_retention'
        ]
        
        for field in fields:
            value = request.form.get(field, '').strip()
            setting = Settings.query.filter_by(key=field).first()
            if setting:
                setting.value = value
            else:
                setting = Settings(key=field, value=value)
                db.session.add(setting)
                
        db.session.commit()
        flash('System settings updated successfully.', 'success')
        return redirect(url_for('settings.settings_view'))
        
    # Fetch settings
    settings_records = Settings.query.all()
    settings_dict = {s.key: s.value for s in settings_records}
    
    # Metadata for configuration dropdowns/tables
    categories = Category.query.all()
    locations = Location.query.all()
    vendors = Vendor.query.all()
    
    return render_template(
        'settings.html',
        settings=settings_dict,
        categories=categories,
        locations=locations,
        vendors=vendors
    )

@settings_bp.route('/category/new', methods=['POST'])
@login_required(role=['admin', 'manager'])
def add_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Category Name is required.', 'danger')
        return redirect(url_for('settings.settings_view'))
        
    if Category.query.filter_by(name=name).first():
        flash(f"Category '{name}' already exists.", 'danger')
        return redirect(url_for('settings.settings_view'))
        
    cat = Category(name=name, description=description)
    db.session.add(cat)
    db.session.commit()
    
    flash(f"Category '{name}' created successfully.", 'success')
    return redirect(url_for('settings.settings_view'))

@settings_bp.route('/location/new', methods=['POST'])
@login_required(role=['admin', 'manager'])
def add_location():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Location Name is required.', 'danger')
        return redirect(url_for('settings.settings_view'))
        
    if Location.query.filter_by(name=name).first():
        flash(f"Location '{name}' already exists.", 'danger')
        return redirect(url_for('settings.settings_view'))
        
    loc = Location(name=name, description=description)
    db.session.add(loc)
    db.session.commit()
    
    flash(f"Location '{name}' created successfully.", 'success')
    return redirect(url_for('settings.settings_view'))

@settings_bp.route('/vendor/new', methods=['POST'])
@login_required(role=['admin', 'manager'])
def add_vendor():
    name = request.form.get('name', '').strip()
    contact_person = request.form.get('contact_person', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    if not name:
        flash('Vendor Name is required.', 'danger')
        return redirect(url_for('settings.settings_view'))
        
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
    return redirect(url_for('settings.settings_view'))
