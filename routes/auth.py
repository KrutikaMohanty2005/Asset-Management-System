from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import User, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Login Decorator helper
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Check user role if required
            if role:
                user_role = session.get('role')
                if isinstance(role, list):
                    if user_role not in role:
                        flash('Unauthorized access: Insufficient permissions.', 'danger')
                        return redirect(url_for('dashboard.view_dashboard'))
                elif user_role != role:
                    flash('Unauthorized access: Insufficient permissions.', 'danger')
                    return redirect(url_for('dashboard.view_dashboard'))
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.view_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Set session variables
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard.view_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
