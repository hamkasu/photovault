from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from photovault.models import Photo, User, db
from sqlalchemy import func
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page - redirect to dashboard if authenticated"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """Company about page"""
    return render_template('about.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with statistics and recent photos"""
    
    # Get user's recent photos
    user_photos = Photo.query.filter_by(user_id=current_user.id)\
                            .order_by(Photo.uploaded_at.desc())\
                            .limit(12).all()
    
    # Calculate user statistics
    total_photos = Photo.query.filter_by(user_id=current_user.id).count()
    edited_photos = Photo.query.filter_by(user_id=current_user.id)\
                              .filter(Photo.edited_filename.isnot(None)).count()
    
    # Calculate total storage used by user
    total_size_result = db.session.query(func.sum(Photo.file_size))\
                                 .filter_by(user_id=current_user.id).scalar()
    total_size = total_size_result or 0
    
    # Create stats object for template
    stats = {
        'total_photos': total_photos,
        'edited_photos': edited_photos,
        'original_photos': total_photos - edited_photos,
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size > 0 else 0,
        'total_users': User.query.count() if current_user.is_admin else None,
        'storage_usage_percent': min(100, (total_size / (100 * 1024 * 1024)) * 100) if total_size > 0 else 0
    }
    
    return render_template('dashboard.html', photos=user_photos, stats=stats)

@main_bp.route('/originals')
@login_required
def originals():
    """View all original photos for the current user"""
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of photos per page
    
    photos = Photo.query.filter_by(user_id=current_user.id)\
                       .order_by(Photo.uploaded_at.desc())\
                       .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('originals.html', photos=photos)

@main_bp.route('/photo/<int:photo_id>')
@login_required
def view_photo(photo_id):
    """View a specific photo"""
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    return render_template('view_photo.html', photo=photo)

@main_bp.route('/upload')
@login_required
def upload():
    """Upload page for photos"""
    return render_template('upload.html')

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_stats = {
        'total_photos': Photo.query.filter_by(user_id=current_user.id).count(),
        'edited_photos': Photo.query.filter_by(user_id=current_user.id)
                                  .filter(Photo.edited_filename.isnot(None)).count(),
        'total_size': db.session.query(func.sum(Photo.file_size))
                               .filter_by(user_id=current_user.id).scalar() or 0,
        'member_since': current_user.created_at.strftime('%B %Y')
    }
    
    return render_template('profile.html', stats=user_stats)