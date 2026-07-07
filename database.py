import pymysql
from models import db, User, Category, Location, Vendor, Settings
import os

def init_db(app):
    db_type = app.config.get('DB_TYPE', 'mysql')
    
    if db_type == 'mysql':
        mysql_user = app.config.get('MYSQL_USER', 'root')
        mysql_password = app.config.get('MYSQL_PASSWORD', 'root')
        mysql_host = app.config.get('MYSQL_HOST', 'localhost')
        mysql_port = int(app.config.get('MYSQL_PORT', '3306'))
        mysql_db = app.config.get('MYSQL_DB', 'asset_management')
        
        try:
            # Connect to MySQL Server without specifying DB to create it if not exists
            conn = pymysql.connect(
                host=mysql_host,
                user=mysql_user,
                password=mysql_password,
                port=mysql_port
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.close()
            conn.close()
            print(f"[Database] Successfully verified or created MySQL database '{mysql_db}'")
        except Exception as e:
            print(f"[Database Warning] Failed to connect to MySQL: {e}")
            print("[Database Warning] Falling back to local SQLite database...")
            # Modify app config for SQLite fallback
            app.config['DB_TYPE'] = 'sqlite'
            sqlite_path = os.path.join(app.config.get('BASE_DIR', ''), app.config.get('SQLITE_DB_PATH', 'asset_management.db'))
            app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
    
    # Initialize SQLAlchemy with the Flask App
    db.init_app(app)
    
    # Create all tables and seed initial data
    with app.app_context():
        db.create_all()
        seed_initial_data()

def seed_initial_data():
    # 1. Seed Admin User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@company.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("[Database Seeding] Created default admin user: admin / admin123")
        
    # Seed Manager User
    if not User.query.filter_by(username='manager').first():
        manager = User(username='manager', email='manager@company.com', role='manager')
        manager.set_password('manager123')
        db.session.add(manager)
        print("[Database Seeding] Created default manager user: manager / manager123")

    # 2. Seed Default Categories
    default_categories = [
        {"name": "IT Hardware", "description": "Laptops, Desktops, Servers, etc."},
        {"name": "Mobile Devices", "description": "Smartphones, Tablets, etc."},
        {"name": "Office Furniture", "description": "Desks, Chairs, Tables, etc."},
        {"name": "Network Equipment", "description": "Routers, Switches, Access Points, etc."},
        {"name": "Software Licenses", "description": "Operating Systems, IDEs, subscriptions"}
    ]
    for cat_data in default_categories:
        if not Category.query.filter_by(name=cat_data["name"]).first():
            category = Category(name=cat_data["name"], description=cat_data["description"])
            db.session.add(category)
            
    # 3. Seed Default Locations
    default_locations = [
        {"name": "Headquarters (HQ)", "description": "Main corporate office"},
        {"name": "Warehouse A", "description": "Primary storage facility"},
        {"name": "Branch Office (East)", "description": "Regional sales and support"},
        {"name": "Remote", "description": "Work from home setup"}
    ]
    for loc_data in default_locations:
        if not Location.query.filter_by(name=loc_data["name"]).first():
            location = Location(name=loc_data["name"], description=loc_data["description"])
            db.session.add(location)

    # 4. Seed Default Vendor
    if not Vendor.query.filter_by(name="Tech Solutions Inc.").first():
        default_vendor = Vendor(
            name="Tech Solutions Inc.",
            contact_person="John Doe",
            email="sales@techsolutions.com",
            phone="+1-555-0199",
            address="123 Technology Drive, Suite 100, Silicon Valley, CA"
        )
        db.session.add(default_vendor)

    # 5. Seed Default Settings
    default_settings = {
        "company_name": "AssetCorp Industries",
        "currency": "USD ($)",
        "timezone": "UTC",
        "email_sender": "alerts@assetcorp.com",
        "email_smtp_server": "smtp.mailtrap.io",
        "email_smtp_port": "2525",
        "roles_list": "admin,manager,staff",
        "backup_frequency": "Daily",
        "backup_retention": "30 Days"
    }
    
    for key, value in default_settings.items():
        if not Settings.query.filter_by(key=key).first():
            setting = Settings(key=key, value=value)
            db.session.add(setting)

    db.session.commit()
    print("[Database Seeding] Completed initialization and seeding successfully.")
