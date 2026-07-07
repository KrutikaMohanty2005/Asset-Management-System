from flask import Blueprint, render_template
from routes.auth import login_required
from models import db, Asset, MaintenanceLog, AssetAssignment
from datetime import datetime, timedelta

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
@login_required()
def list_notifications():
    notifications = []
    
    # Warranty expiring soon (within 30 days)
    upcoming_warranty = Asset.query.filter(
        Asset.warranty_expiry.isnot(None),
        Asset.warranty_expiry <= datetime.utcnow().date() + timedelta(days=30),
        Asset.warranty_expiry >= datetime.utcnow().date()
    ).all()
    
    for asset in upcoming_warranty:
        notifications.append({
            'type': 'warning',
            'icon': 'fa-shield-halved',
            'title': f"Warranty expiring soon: {asset.name}",
            'detail': f"Asset {asset.asset_id} warranty expires on {asset.warranty_expiry.strftime('%Y-%m-%d')}",
            'date': asset.warranty_expiry
        })
    
    # Pending maintenance
    pending_maint = MaintenanceLog.query.filter(
        MaintenanceLog.status.in_(['Requested', 'In Progress'])
    ).all()
    
    for log in pending_maint:
        notifications.append({
            'type': 'info',
            'icon': 'fa-screwdriver-wrench',
            'title': f"Maintenance {log.status}: {log.asset.name}",
            'detail': f"Asset {log.asset.asset_id} - {log.remarks or 'No remarks'}",
            'date': log.request_date
        })
    
    # Overdue warranty (expired)
    expired_warranty = Asset.query.filter(
        Asset.warranty_expiry.isnot(None),
        Asset.warranty_expiry < datetime.utcnow().date(),
        Asset.status != 'Retired'
    ).all()
    
    for asset in expired_warranty:
        notifications.append({
            'type': 'danger',
            'icon': 'fa-circle-exclamation',
            'title': f"Warranty expired: {asset.name}",
            'detail': f"Asset {asset.asset_id} warranty expired on {asset.warranty_expiry.strftime('%Y-%m-%d')}",
            'date': asset.warranty_expiry
        })
    
    # Sort by date descending
    notifications.sort(key=lambda x: x['date'] if x['date'] else datetime.min.date(), reverse=True)
    
    return render_template('notifications/list.html', notifications=notifications)
