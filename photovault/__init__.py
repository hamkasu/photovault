# photovault/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# --- Added imports for Rate Limiting ---
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# --- End Added imports ---
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
# --- Initialize Limiter ---
limiter = Limiter(
    key_func=get_remote_address, # Limit by client IP address
    default_limits=["200 per day", "50 per hour"] # Global default limits
)
# --- End Initialize Limiter ---

def create_app():
    app = Flask(__name__)
    
    # --- Security Configuration ---
    # Use a strong secret key from environment variable
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    
    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///photovault.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # File Uploads
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'photovault/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)) # 16MB default
    
    # --- Session Security (adjusted for development) ---
    # Only enable HTTPS-only cookies in production
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True # Prevent JavaScript access to session cookie
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Protect against CSRF (can be 'Strict' for higher security)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    # --- Initialize Limiter with the app ---
    limiter.init_app(app)
    # --- End Initialize Limiter ---

    # Register blueprints
    from photovault.routes.auth import auth_bp
    from photovault.routes.main import main_bp
    from photovault.routes.photo import photo_bp
    from photovault.routes.admin import admin_bp  # Added missing import
    from photovault.routes.superuser import superuser_bp  # Added missing import
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(photo_bp)
    app.register_blueprint(admin_bp)  # Added missing registration
    app.register_blueprint(superuser_bp)  # Added missing registration
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    # --- Add Security Headers ---
    @app.after_request
    def add_security_headers(response):
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Clickjacking protection
        response.headers['X-Frame-Options'] = 'DENY'
        # XSS Protection (deprecated but still used by some browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # For production, if using HTTPS, uncomment the following:
        if os.getenv('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    # --- End Security Headers ---
    
    return app