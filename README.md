# Asset Management System (AMS)

A full-featured web-based Asset Management System built with Flask, designed to help organizations track, manage, and monitor their physical and digital assets throughout their lifecycle.

## Features

- **Dashboard** - Real-time overview of all assets with charts and recent activity
- **Asset Management** - Add, edit, delete, and view detailed asset information
- **Categories** - Organize assets by category (Laptops, Desktops, Printers, etc.)
- **Employees** - Manage employee records and track assigned assets
- **Vendors** - Maintain vendor/supplier contact information
- **Asset Assignment** - Assign available assets to employees with logging
- **Return Assets** - Check-in and return assigned assets
- **Maintenance Logs** - Track repair requests, service history, and costs
- **QR Code Scanner** - Scan QR codes for quick asset lookup and actions
- **Reports** - Analytics and summaries for asset statistics
- **Notifications** - System alerts for warranty expiry and pending maintenance
- **User Management** - Role-based access control (Admin, Manager, Staff)
- **Settings** - Configure company info, email, and manage categories/locations/vendors

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Database:** MySQL / SQLite (fallback)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **Icons:** Font Awesome 6
- **Fonts:** Inter (Google Fonts)

## Installation

### Prerequisites

- Python 3.8+
- MySQL Server (optional - SQLite works as fallback)
- pip

### Steps

1. Clone the repository:
```bash
git clone https://github.com/KrutikaMohanty2005/Asset-Management-System.git
cd Asset-Management-System
```

2. Install dependencies:
```bash
pip install flask flask-sqlalchemy pymysql python-dotenv werkzeug
```

3. Configure environment (optional for MySQL):
Edit `.env` file:
```
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=asset_management
```

4. Run the application:
```bash
python app.py
```

5. Open browser and visit:
```
http://127.0.0.1:5000
```

## Default Login

| Username | Password | Role    |
|----------|----------|---------|
| admin    | admin123 | Admin   |
| manager  | manager123 | Manager |

## Project Structure

```
Asset-Management-System/
├── app.py                  # Flask application entry point
├── config.py               # Configuration settings
├── database.py             # Database initialization and seeding
├── models.py               # SQLAlchemy database models
├── .env                    # Environment variables
├── routes/
│   ├── auth.py             # Login/logout authentication
│   ├── dashboard.py        # Dashboard and chart data
│   ├── assets.py           # Asset CRUD operations
│   ├── employees.py        # Employee management
│   ├── categories.py       # Category management
│   ├── vendors.py          # Vendor management
│   ├── asset_assignment.py # Asset assignment to employees
│   ├── return_assets.py    # Asset return/check-in
│   ├── maintenance.py      # Maintenance log management
│   ├── qr.py               # QR code scanner and actions
│   ├── reports.py          # Reports and analytics
│   ├── notifications.py    # System notifications
│   ├── users.py            # User account management
│   └── settings.py         # System settings
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout with sidebar
│   ├── dashboard.html      # Dashboard page
│   ├── auth/               # Login page
│   ├── assets/             # Asset list, add/edit, details
│   ├── employees/          # Employee management
│   ├── categories/         # Category management
│   ├── vendors/            # Vendor management
│   ├── asset_assignment/   # Assignment page
│   ├── return_assets/      # Return assets page
│   ├── maintenance/        # Maintenance logs
│   ├── qr/                 # QR scanner and result
│   ├── reports/            # Reports page
│   ├── notifications/      # Notifications page
│   ├── users/              # User management
│   └── settings.html       # System settings
├── static/
│   ├── css/style.css       # Custom stylesheet
│   └── js/
│       ├── main.js         # Theme toggle and utilities
│       ├── charts.js       # Dashboard chart initialization
│       └── scanner.js      # QR scanner controller
└── static/uploads/         # Uploaded files (images, invoices)
```

## Database Schema

- **users** - System user accounts with roles
- **categories** - Asset categories
- **locations** - Physical locations
- **vendors** - Vendor/supplier records
- **employees** - Employee records
- **assets** - Asset inventory with full details
- **asset_assignments** - Assignment history log
- **maintenance_logs** - Maintenance service records
- **settings** - Application configuration key-value pairs

## License

This project is for educational and internship purposes.
