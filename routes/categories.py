from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, Category, Asset

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/', methods=['GET', 'POST'])
@login_required()
def list_categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('categories.list_categories'))
            
        if Category.query.filter_by(name=name).first():
            flash(f"Category '{name}' already exists.", 'danger')
            return redirect(url_for('categories.list_categories'))
            
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        
        flash(f"Category '{name}' created successfully.", 'success')
        return redirect(url_for('categories.list_categories'))
        
    categories = Category.query.all()
    return render_template('categories/list.html', categories=categories)

@categories_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required(role=['admin', 'manager'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('categories.edit_category', id=id))
            
        existing = Category.query.filter(Category.name == name, Category.id != id).first()
        if existing:
            flash(f"Category '{name}' already exists.", 'danger')
            return redirect(url_for('categories.edit_category', id=id))
            
        category.name = name
        category.description = description
        db.session.commit()
        
        flash(f"Category '{name}' updated successfully.", 'success')
        return redirect(url_for('categories.list_categories'))
        
    return render_template('categories/list.html', categories=Category.query.all(), edit_category=category)

@categories_bp.route('/<int:id>/delete', methods=['POST'])
@login_required(role=['admin', 'manager'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    asset_count = Asset.query.filter_by(category_id=id).count()
    if asset_count > 0:
        flash(f"Cannot delete category '{category.name}' because it has {asset_count} asset(s). Reassign assets first.", 'danger')
        return redirect(url_for('categories.list_categories'))
        
    name = category.name
    db.session.delete(category)
    db.session.commit()
    
    flash(f"Category '{name}' deleted successfully.", 'success')
    return redirect(url_for('categories.list_categories'))
