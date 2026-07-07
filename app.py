from flask import Flask, redirect, url_for, session
from config import Config
from models import db
from database import init_db
import os

# Import Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.assets import assets_bp
from routes.employees import employees_bp
from routes.maintenance import maintenance_bp
from routes.settings import settings_bp
from routes.qr import qr_bp
from routes.categories import categories_bp
from routes.vendors import vendors_bp
from routes.asset_assignment import asset_assignment_bp
from routes.return_assets import return_assets_bp
from routes.reports import reports_bp
from routes.notifications import notifications_bp
from routes.users import users_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure Upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'invoices'), exist_ok=True)
    
    # Initialize Database and seed starter data
    init_db(app)
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(asset_assignment_bp)
    app.register_blueprint(return_assets_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(users_bp)
    
    # Global root redirect helper
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard.view_dashboard'))
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    # Running Flask local dev server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
