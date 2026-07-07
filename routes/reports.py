from flask import Blueprint, render_template, session
from routes.auth import login_required
from models import db, Asset, Employee, MaintenanceLog, AssetAssignment, Category, Vendor, Location
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required()
def reports_view():
    # Asset statistics
    total_assets = Asset.query.count()
    assigned_count = Asset.query.filter_by(status='Assigned').count()
    available_count = Asset.query.filter_by(status='Available').count()
    maintenance_count = Asset.query.filter_by(status='Maintenance').count()
    retired_count = Asset.query.filter_by(status='Retired').count()
    
    # Assets by category
    categories = Category.query.all()
    category_stats = []
    for cat in categories:
        count = Asset.query.filter_by(category_id=cat.id).count()
        category_stats.append({'name': cat.name, 'count': count})
    
    # Assets by location
    locations = Location.query.all()
    location_stats = []
    for loc in locations:
        count = Asset.query.filter_by(location_id=loc.id).count()
        location_stats.append({'name': loc.name, 'count': count})
    
    # Maintenance cost summary
    total_maintenance_cost = db.session.query(func.sum(MaintenanceLog.cost)).filter(
        MaintenanceLog.status == 'Completed'
    ).scalar() or 0
    
    completed_maintenance = MaintenanceLog.query.filter_by(status='Completed').count()
    pending_maintenance = MaintenanceLog.query.filter(MaintenanceLog.status.in_(['Requested', 'In Progress'])).count()
    
    # Employee stats
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(status='Active').count()
    
    # Recent assignments
    recent_assignments = AssetAssignment.query.order_by(
        AssetAssignment.assigned_date.desc()
    ).limit(10).all()
    
    # Vendor stats
    total_vendors = Vendor.query.count()
    
    return render_template(
        'reports/reports.html',
        total_assets=total_assets,
        assigned_count=assigned_count,
        available_count=available_count,
        maintenance_count=maintenance_count,
        retired_count=retired_count,
        category_stats=category_stats,
        location_stats=location_stats,
        total_maintenance_cost=total_maintenance_cost,
        completed_maintenance=completed_maintenance,
        pending_maintenance=pending_maintenance,
        total_employees=total_employees,
        active_employees=active_employees,
        recent_assignments=recent_assignments,
        total_vendors=total_vendors
    )
