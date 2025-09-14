"""
PhotoVault - Professional Photo Management Platform
Copyright (c) 2025 Calmic Sdn Bhd. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution,
modification, or use of this software is strictly prohibited.

Website: https://www.calmic.com.my
Email: support@calmic.com.my

CALMIC SDN BHD - "Committed to Excellence"
"""

import os
from flask import Flask
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# Add this import near the top with other imports
from flask_wtf.csrf import CSRFProtect

# Try to load dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to import company version info, provide fallback if missing
try:
    from photovault.version import (
        get_version, get_version_info, get_full_version, 
        get_company_info, get_app_title, get_copyright
    )
except ImportError:
    # Fallback company functions if version.py is missing
    def get_version():
        return "1.0.0"
    
    def get_version_info():
        return {
            "version": "1.0.0",
            "build": "2025.09.10",
            "author": "Calmic Sdn Bhd",
            "company": "Calmic Sdn Bhd",
            "description": "Professional Photo Storage and Management Platform",
            "website": "https://calmic.com.my",
            "support_email": "postmaster@calmic.com,my"
        }
    
    def get_full_version():
        return "PhotoVault v1.0.0 (Build 2025.09.10) - Calmic Sdn Bhd"
    
    def get_company_info():
        return {
            "name": "Calmic Sdn Bhd",
            "description": "Leading provider of digital solutions and enterprise software",
            "website": "https://calmic.com.my",
            "support_email": "postmaster@calmic.com",
            "address": "Malaysia",
            "established": "2022"
        }
    
    def get_app_title():
        return "PhotoVault by Calmic Sdn Bhd"
    
    def get_copyright():
        return "© 2025 Calmic Sdn Bhd. All rights reserved."

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application"""
    # Configure template and static folder paths relative to photovault package
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    csrf = CSRFProtect()
    csrf.init_app(app)

    # Load production configuration if deployed
    is_production = os.getenv('REPLIT_DEPLOYMENT') == '1'
    if is_production:
        try:
            from config import ProductionConfig
            app.config.from_object(ProductionConfig)
            print("✓ Production configuration loaded")
        except ImportError:
            pass
        
        # Validate critical production settings
        if not app.config.get('SECRET_KEY'):
            secret_key = os.environ.get('SECRET_KEY')
            if not secret_key:
                raise RuntimeError("SECRET_KEY must be set in production environment")
            app.config['SECRET_KEY'] = secret_key
            
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                raise RuntimeError("DATABASE_URL must be set in production environment")
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Development configuration
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        # Use absolute path for SQLite to avoid working directory issues
        sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'photovault.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{sqlite_path}')
    
    # Common configuration
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    
    # Configure database engine options for better PostgreSQL handling
    if 'postgresql' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
        app.config.setdefault('SQLALCHEMY_ENGINE_OPTIONS', {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {
                'connect_timeout': 10,
                'options': '-c timezone=utc'
            }
        })
    # Fix upload folder to be within served static directory
    app.config.setdefault('UPLOAD_FOLDER', os.path.join(static_dir, 'uploads'))
    app.config.setdefault('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB
    
    # Session configuration
    app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
    app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    
    # Create upload folder
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"✓ Upload folder created/verified: {app.config['UPLOAD_FOLDER']}")
    except Exception as e:
        print(f"Warning: Could not create upload folder: {e}")
    
    # Register blueprints
    try:
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
        
        print("✓ All blueprints registered successfully")
    except Exception as e:
        print(f"Warning: Error registering blueprints: {e}")
    
    # Create database tables (skip in production if using migrations)
    with app.app_context():
        try:
            if not is_production:
                # Database tables will be created by migrations in production
                # For development, skip db.create_all() since we use migrations
                print("✓ Database setup: using migrations for schema management")
            else:
                print("✓ Production mode: skipping db.create_all() (use migrations)")
        except Exception as e:
            print(f"Warning: Error with database setup: {e}")
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add production security headers if configured
        if 'SECURITY_HEADERS' in app.config:
            for header, value in app.config['SECURITY_HEADERS'].items():
                response.headers[header] = value
        
        return response
    
    # --- Company Context Processor ---
    @app.context_processor
    def inject_company_context():
        """Make company and version information available to all templates"""
        return {
            'app_version': get_version(),
            'app_version_info': get_version_info(),
            'app_full_version': get_full_version(),
            'company_info': get_company_info(),
            'app_title': get_app_title(),
            'company_copyright': get_copyright()
        }
    
    print("✓ PhotoVault by Calmic Sdn Bhd created successfully")
    return app