from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, User

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/', methods=['GET', 'POST'])
@login_required(role=['admin'])
def list_users():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'staff').strip()
        
        if not username or not email or not password:
            flash('Username, email, and password are required.', 'danger')
            return redirect(url_for('users.list_users'))
            
        if User.query.filter_by(username=username).first():
            flash(f"Username '{username}' already exists.", 'danger')
            return redirect(url_for('users.list_users'))
            
        if User.query.filter_by(email=email).first():
            flash(f"Email '{email}' is already registered.", 'danger')
            return redirect(url_for('users.list_users'))
            
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash(f"User '{username}' created successfully.", 'success')
        return redirect(url_for('users.list_users'))
        
    users = User.query.all()
    return render_template('users/list.html', users=users)

@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required(role=['admin'])
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'staff').strip()
        password = request.form.get('password', '').strip()
        
        if not email:
            flash('Email is required.', 'danger')
            return redirect(url_for('users.edit_user', id=id))
            
        existing_email = User.query.filter(User.email == email, User.id != id).first()
        if existing_email:
            flash(f"Email '{email}' is already in use.", 'danger')
            return redirect(url_for('users.edit_user', id=id))
            
        user.email = email
        user.role = role
        if password:
            user.set_password(password)
            
        db.session.commit()
        flash(f"User '{user.username}' updated successfully.", 'success')
        return redirect(url_for('users.list_users'))
        
    return render_template('users/list.html', users=User.query.all(), edit_user=user)

@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required(role=['admin'])
def delete_user(id):
    user = User.query.get_or_404(id)
    
    if user.username == 'admin':
        flash('Cannot delete the default admin user.', 'danger')
        return redirect(url_for('users.list_users'))
        
    name = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User '{name}' deleted successfully.", 'success')
    return redirect(url_for('users.list_users'))
