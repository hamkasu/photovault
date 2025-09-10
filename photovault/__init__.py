# photovault/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Try to import version, provide fallback if missing
try:
    from photovault.version import get_version, get_version_info, get_full_version
except ImportError:
    # Fallback version functions if version.py is missing
    def get_version():
        return "1.0.0"
    
    def get_version_info():
        return {
            "version": "1.0.0",
            "build": "2025.09.10",
            "author": "PhotoVault Team",
            "description": "Personal Photo Storage and Editing Platform"
        }
    
    def get_full_version():
        return "PhotoVault v1.0.0 (Build 2025.09.10)"

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # --- Security Configuration ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    
    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///photovault.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # File Uploads
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'photovault/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)) # 16MB default
    
    # --- Session Security ---
    # Detect Railway production environment
    is_production = (
        os.getenv('FLASK_ENV') == 'production' or 
        os.getenv('ENVIRONMENT') == 'production' or 
        os.getenv('RAILWAY_ENVIRONMENT_NAME') is not None
    )
    
    app.config['SESSION_COOKIE_SECURE'] = is_production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    # Register blueprints
    from photovault.routes.auth import auth_bp
    from photovault.routes.main import main_bp
    from photovault.routes.photo import photo_bp
    from photovault.routes.admin import admin_bp
    from photovault.routes.superuser import superuser_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(photo_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(superuser_bp)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    # --- Security Headers ---
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        if is_production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    # --- Version Context Processor ---
    @app.context_processor
    def inject_version():
        """Make version information available to all templates"""
        return {
            'app_version': get_version(),
            'app_version_info': get_version_info(),
            'app_full_version': get_full_version()
        }
    
    return app