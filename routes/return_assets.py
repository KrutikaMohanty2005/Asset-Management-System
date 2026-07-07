from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, Asset, AssetAssignment
from datetime import datetime

return_assets_bp = Blueprint('return_assets', __name__, url_prefix='/return-assets')

@return_assets_bp.route('/', methods=['GET', 'POST'])
@login_required()
def list_returns():
    if request.method == 'POST':
        asset_id = request.form.get('asset_id')
        
        if not asset_id:
            flash('Please select an asset to return.', 'danger')
            return redirect(url_for('return_assets.list_returns'))
            
        asset = Asset.query.get(int(asset_id))
        if not asset:
            flash('Asset not found.', 'danger')
            return redirect(url_for('return_assets.list_returns'))
            
        if asset.status != 'Assigned':
            flash(f"Asset '{asset.name}' is not currently assigned.", 'danger')
            return redirect(url_for('return_assets.list_returns'))
            
        # Find active assignment
        active_ass = AssetAssignment.query.filter_by(asset_id=asset.id, returned_date=None).first()
        if active_ass:
            active_ass.returned_date = datetime.utcnow()
            active_ass.notes = f"{active_ass.notes or ''} [Returned via Return Assets page]."
            
        asset.status = 'Available'
        asset.assigned_employee_id = None
        db.session.commit()
        
        flash(f"Asset '{asset.name}' has been returned successfully.", 'success')
        return redirect(url_for('return_assets.list_returns'))
        
    assigned_assets = Asset.query.filter_by(status='Assigned').all()
    recent_returns = AssetAssignment.query.filter(
        AssetAssignment.returned_date.isnot(None)
    ).order_by(AssetAssignment.returned_date.desc()).limit(20).all()
    
    return render_template(
        'return_assets/list.html',
        assigned_assets=assigned_assets,
        recent_returns=recent_returns
    )
