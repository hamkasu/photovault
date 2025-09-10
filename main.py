# photovault/routes/main.py
from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user
from photovault.models import Photo

# Try to import version, provide fallback if missing
try:
    from photovault.version import get_version_info, VERSION_HISTORY
except ImportError:
    # Fallback version functions if version.py is missing
    def get_version_info():
        return {
            "version": "1.0.0",
            "build": "2025.09.10",
            "author": "PhotoVault Team",
            "description": "Personal Photo Storage and Editing Platform"
        }
    
    VERSION_HISTORY = {
        "1.0.0": {
            "date": "2025-09-10",
            "changes": [
                "Initial release",
                "Photo upload and storage",
                "Basic photo editing tools",
                "User authentication system",
                "Admin panel with user management",
                "Statistics dashboard",
                "Role-based access control"
            ]
        }
    }

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # This will show the "active" version (edited if exists, otherwise original)
    user_photos = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.uploaded_at.desc()).all()
    return render_template('dashboard.html', photos=user_photos)

# --- New route for Original Images ---
@main_bp.route('/originals')
@login_required
def originals():
    # Fetch all photos for the user. The template will display the original file (photo.filename).
    user_photos = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.uploaded_at.desc()).all()
    return render_template('originals.html', photos=user_photos)
# --- End New route ---

@main_bp.route('/editor/<int:photo_id>')
@login_required
def editor(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        abort(403) # More explicit than redirect
    return render_template('editor.html', photo=photo)

@main_bp.route('/about')
def about():
    """About page with version information"""
    version_info = get_version_info()
    return render_template('about.html', version_info=version_info, version_history=VERSION_HISTORY)

app = create_app()

# CLI Commands for easier management
@app.cli.command()
@click.option('--username', prompt='Username', help='The username for the superuser')
@click.option('--email', prompt='Email', help='The email for the superuser')
@click.option('--password', prompt='Password', hide_input=True, confirmation_prompt=True, help='The password for the superuser')
def create_superuser(username, email, password):
    """Create a superuser."""
    from photovault.models import User
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            click.echo(f'Error: User with username "{username}" or email "{email}" already exists.')
            return
        
        # Create superuser
        user = User(
            username=username,
            email=email,
            is_superuser=True,
            is_admin=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'Superuser "{username}" created successfully!')

@app.cli.command()
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        click.echo('Database initialized!')

@app.cli.command()
def version():
    """Show PhotoVault version information."""
    version_info = get_version_info()
    click.echo('=== PhotoVault Version Information ===')
    click.echo(f'Version: {version_info["version"]}')
    click.echo(f'Build: {version_info["build"]}')
    click.echo(f'Description: {version_info["description"]}')
    click.echo(f'Author: {version_info["author"]}')
    click.echo('')
    click.echo('=== Latest Changes ===')
    latest_version = max(VERSION_HISTORY.keys())
    changes = VERSION_HISTORY[latest_version]["changes"]
    for change in changes:
        click.echo(f'• {change}')

@app.cli.command()
def info():
    """Show brief version and system info."""
    click.echo(get_full_version())

@app.cli.command()
def stats():
    """Show database statistics."""
    from photovault.models import User, Photo
    
    with app.app_context():
        user_count = User.query.count()
        admin_count = User.query.filter_by(is_admin=True).count()
        superuser_count = User.query.filter_by(is_superuser=True).count()
        
        all_photos = Photo.query.all()
        photo_count = len(all_photos)
        edited_count = sum(1 for photo in all_photos if photo.edited_filename is not None)
        total_size = sum(photo.file_size or 0 for photo in all_photos)
        
        click.echo(f'=== PhotoVault Statistics - {get_full_version()} ===')
        click.echo(f'Users: {user_count} (Admins: {admin_count}, Superusers: {superuser_count})')
        click.echo(f'Photos: {photo_count} (Edited: {edited_count})')
        click.echo(f'Storage: {total_size / 1024 / 1024:.2f} MB')

@app.cli.command()
@click.argument('username')
def make_admin(username):
    """Make a user an admin."""
    from photovault.models import User
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo(f'Error: User "{username}" not found.')
            return
        
        user.is_admin = True
        db.session.commit()
        click.echo(f'User "{username}" is now an admin!')

@app.cli.command()
@click.argument('username')
def make_superuser(username):
    """Make a user a superuser."""
    from photovault.models import User
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo(f'Error: User "{username}" not found.')
            return
        
        user.is_superuser = True
        user.is_admin = True  # Superusers are automatically admins
        db.session.commit()
        click.echo(f'User "{username}" is now a superuser!')

@app.cli.command()
def list_users():
    """List all users with their roles."""
    from photovault.models import User
    
    with app.app_context():
        users = User.query.order_by(User.created_at.desc()).all()
        
        if not users:
            click.echo('No users found.')
            return
        
        click.echo('=== All Users ===')
        for user in users:
            role = 'Superuser' if user.is_superuser else 'Admin' if user.is_admin else 'User'
            click.echo(f'{user.id:3d} | {user.username:20} | {user.email:30} | {role}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)