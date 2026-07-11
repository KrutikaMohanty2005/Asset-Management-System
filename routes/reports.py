from flask import Blueprint, render_template, session, Response
from routes.auth import login_required
from models import db, Asset, Employee, MaintenanceLog, AssetAssignment, Category, Vendor, Location
from sqlalchemy import func
import csv
import io

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

@reports_bp.route('/export/assets')
@login_required()
def export_assets_csv():
    assets = Asset.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Asset ID', 'Name', 'Category', 'Brand/Model', 'Serial Number', 'Purchase Date', 'Purchase Cost', 'Warranty Expiry', 'Location', 'Status', 'Assigned To', 'Vendor'])
    for asset in assets:
        writer.writerow([
            asset.asset_id,
            asset.name,
            asset.category.name if asset.category else '',
            asset.brand_model or '',
            asset.serial_number or '',
            asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else '',
            asset.purchase_cost or '',
            asset.warranty_expiry.strftime('%Y-%m-%d') if asset.warranty_expiry else '',
            asset.location.name if asset.location else '',
            asset.status,
            asset.assigned_employee.name if asset.assigned_employee else 'Unassigned',
            asset.vendor.name if asset.vendor else ''
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=assets_report.csv'}
    )

@reports_bp.route('/export/maintenance')
@login_required()
def export_maintenance_csv():
    logs = MaintenanceLog.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Asset ID', 'Asset Name', 'Request Date', 'Service Date', 'Vendor', 'Cost', 'Status', 'Remarks'])
    for log in logs:
        writer.writerow([
            log.asset.asset_id if log.asset else '',
            log.asset.name if log.asset else '',
            log.request_date.strftime('%Y-%m-%d %H:%M') if log.request_date else '',
            log.service_date.strftime('%Y-%m-%d %H:%M') if log.service_date else '',
            log.vendor.name if log.vendor else '',
            log.cost or '',
            log.status,
            log.remarks or ''
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=maintenance_report.csv'}
    )

@reports_bp.route('/export/employees')
@login_required()
def export_employees_csv():
    employees = Employee.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Employee ID', 'Name', 'Department', 'Designation', 'Email', 'Contact', 'Status', 'Assigned Assets'])
    for emp in employees:
        assigned_count = Asset.query.filter_by(assigned_employee_id=emp.id, status='Assigned').count()
        writer.writerow([
            emp.employee_id,
            emp.name,
            emp.department or '',
            emp.designation or '',
            emp.email,
            emp.contact or '',
            emp.status,
            assigned_count
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=employees_report.csv'}
    )
