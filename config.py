import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key-ams-827361')
    
    # Upload Settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

    # Database Configuration
    DB_TYPE = os.getenv('DB_TYPE', 'mysql').lower()
    
    # MySQL Settings
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DB = os.getenv('MYSQL_DB', 'asset_management')
    
    # SQLite Settings
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'asset_management.db')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DB_TYPE == 'mysql':
            # Format: mysql+pymysql://username:password@host:port/database
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        else:
            return f"sqlite:///{os.path.join(self.BASE_DIR, self.SQLITE_DB_PATH)}"
            
    SQLALCHEMY_TRACK_MODIFICATIONS = False
