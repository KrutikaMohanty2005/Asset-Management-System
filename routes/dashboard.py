from flask import Blueprint, render_template, jsonify, session
from routes.auth import login_required
from models import db, Asset, Employee, MaintenanceLog, AssetAssignment, Category, Vendor
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required()
def view_dashboard():
    # Counts
    total_assets = Asset.query.count()
    assigned_assets = Asset.query.filter_by(status='Assigned').count()
    available_assets = Asset.query.filter_by(status='Available').count()
    maintenance_assets = Asset.query.filter_by(status='Maintenance').count()
    retired_assets = Asset.query.filter_by(status='Retired').count()
    
    # Percentages
    assigned_pct = round((assigned_assets / total_assets * 100), 2) if total_assets > 0 else 0
    available_pct = round((available_assets / total_assets * 100), 2) if total_assets > 0 else 0
    maintenance_pct = round((maintenance_assets / total_assets * 100), 2) if total_assets > 0 else 0
    
    # Recent Activities compiled timeline
    recent_assignments = AssetAssignment.query.order_by(AssetAssignment.assigned_date.desc()).limit(10).all()
    recent_maintenance = MaintenanceLog.query.order_by(MaintenanceLog.request_date.desc()).limit(10).all()
    
    timeline_activities = []
    
    for ass in recent_assignments:
        if ass.returned_date:
            timeline_activities.append({
                'type': 'return',
                'title': f"{ass.asset.name} ({ass.asset.asset_id}) returned by {ass.employee.name}",
                'detail': f"{ass.employee.name} returned the asset",
                'date': ass.returned_date,
                'icon': 'fa-rotate-left',
                'color': '#34d399'
            })
        else:
            timeline_activities.append({
                'type': 'assignment',
                'title': f"{ass.asset.name} ({ass.asset.asset_id}) assigned to {ass.employee.name}",
                'detail': f"Assigned by {ass.assigner.username}",
                'date': ass.assigned_date,
                'icon': 'fa-user-plus',
                'color': '#60a5fa'
            })
    
    for maint in recent_maintenance:
        if maint.status == 'Completed':
            timeline_activities.append({
                'type': 'maintenance_complete',
                'title': f"{maint.asset.name} ({maint.asset.asset_id}) maintenance completed",
                'detail': f"Cost: ${maint.cost or 0:.2f}",
                'date': maint.service_date or maint.request_date,
                'icon': 'fa-check-circle',
                'color': '#34d399'
            })
        elif maint.status in ['Requested', 'In Progress']:
            timeline_activities.append({
                'type': 'maintenance',
                'title': f"{maint.asset.name} ({maint.asset.asset_id}) under maintenance",
                'detail': maint.remarks or 'Maintenance in progress',
                'date': maint.request_date,
                'icon': 'fa-wrench',
                'color': '#fbbf24'
            })
    
    # Sort timeline by date descending
    timeline_activities = sorted(timeline_activities, key=lambda x: x['date'], reverse=True)[:8]
    
    # Recent Assets
    recent_assets = Asset.query.order_by(Asset.created_at.desc()).limit(5).all()
    
    return render_template(
        'dashboard.html',
        total_assets=total_assets,
        assigned_assets=assigned_assets,
        available_assets=available_assets,
        maintenance_assets=maintenance_assets,
        retired_assets=retired_assets,
        assigned_pct=assigned_pct,
        available_pct=available_pct,
        maintenance_pct=maintenance_pct,
        activities=timeline_activities,
        recent_assets=recent_assets
    )

@dashboard_bp.route('/api/dashboard/chart-data')
@login_required()
def chart_data():
    # 1. Assets by Category
    categories = Category.query.all()
    cat_labels = []
    cat_counts = []
    for cat in categories:
        count = Asset.query.filter_by(category_id=cat.id).count()
        if count > 0:
            cat_labels.append(cat.name)
            cat_counts.append(count)
    
    # 2. Assets by Status
    total = Asset.query.count()
    assigned = Asset.query.filter_by(status='Assigned').count()
    available = Asset.query.filter_by(status='Available').count()
    maintenance = Asset.query.filter_by(status='Maintenance').count()
    
    status_labels = ['Assigned', 'Available', 'Maintenance']
    status_counts = [assigned, available, maintenance]
    
    return jsonify({
        'categories': {
            'labels': cat_labels,
            'counts': cat_counts
        },
        'status': {
            'labels': status_labels,
            'counts': status_counts
        }
    })
