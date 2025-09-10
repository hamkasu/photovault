# photovault/__init__.py (Alternative - With Flask-Limiter configured)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
from photovault.version import get_version, get_version_info, get_full_version

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///photovault.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'photovault/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # Detect production environment
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
    
    # Configure Flask-Limiter with Redis or fallback to memory
    redis_url = os.getenv('REDIS_URL')
    if redis_url and is_production:
        # Use Redis in production if available
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=redis_url
        )
    else:
        # Use memory storage but suppress warnings for development
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://",
            # Suppress warnings in development
            headers_enabled=not is_production
        )

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
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        if is_production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    # Version context processor
    @app.context_processor
    def inject_version():
        return {
            'app_version': get_version(),
            'app_version_info': get_version_info(),
            'app_full_version': get_full_version()
        }
    
    return app