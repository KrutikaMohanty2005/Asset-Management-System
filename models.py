from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff') # admin, manager, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignments_created = db.relationship('AssetAssignment', backref='assigner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    assets = db.relationship('Asset', backref='category', lazy=True)


class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    assets = db.relationship('Asset', backref='location', lazy=True)


class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Relationships
    assets = db.relationship('Asset', backref='vendor', lazy=True)
    maintenance_logs = db.relationship('MaintenanceLog', backref='vendor', lazy=True)


class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    contact = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assets = db.relationship('Asset', backref='assigned_employee', lazy=True)
    assignments = db.relationship('AssetAssignment', backref='employee', lazy=True)


class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand_model = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_cost = db.Column(db.Numeric(10, 2), nullable=True)
    warranty_expiry = db.Column(db.Date, nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    assigned_employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Available') # Available, Assigned, Maintenance, Retired
    invoice_path = db.Column(db.String(255), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    qr_code_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('AssetAssignment', backref='asset', cascade="all, delete-orphan", lazy=True)
    maintenance_logs = db.relationship('MaintenanceLog', backref='asset', cascade="all, delete-orphan", lazy=True)


class AssetAssignment(db.Model):
    __tablename__ = 'asset_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    returned_date = db.Column(db.DateTime, nullable=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)


class MaintenanceLog(db.Model):
    __tablename__ = 'maintenance_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    service_date = db.Column(db.DateTime, nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Requested') # Requested, In Progress, Completed, Cancelled
    next_maintenance_date = db.Column(db.Date, nullable=True)


class Settings(db.Model):
    __tablename__ = 'settings'
    
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=False)
