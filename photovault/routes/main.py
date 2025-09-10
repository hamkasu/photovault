# photovault/routes/main.py
from flask import Blueprint, render_template, redirect, url_for, abort # Added abort
from flask_login import login_required, current_user
from photovault.models import Photo

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
