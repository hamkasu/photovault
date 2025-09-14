"""
PhotoVault - Professional Photo Management Platform
Copyright (c) 2025 Calmic Sdn Bhd. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution,
modification, or use of this software is strictly prohibited.

Website: https://www.calmic.com.my
Email: support@calmic.com.my

CALMIC SDN BHD - "Committed to Excellence"
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from photovault.models import Photo, User, Person, PhotoPerson, db
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
    """View a specific photo with people tagging"""
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    
    # Get all people for this user (for tagging dropdown)
    all_people = Person.query.filter_by(user_id=current_user.id).order_by(Person.name).all()
    
    # Get people already tagged in this photo
    tagged_people_records = PhotoPerson.query.filter_by(photo_id=photo.id).all()
    tagged_people = []
    for record in tagged_people_records:
        person = Person.query.get(record.person_id)
        if person:
            tagged_people.append({
                'person': person,
                'record': record
            })
    
    return render_template('view_photo.html', 
                         photo=photo, 
                         all_people=all_people, 
                         tagged_people=tagged_people)

@main_bp.route('/editor/<int:photo_id>')
@login_required
def editor(photo_id):
    """Photo editor for markup and editing"""
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    return render_template('editor.html', photo=photo)

@main_bp.route('/people')
@login_required
def people():
    """Manage people for tagging photos"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    people = Person.query.filter_by(user_id=current_user.id)\
                        .order_by(Person.name)\
                        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Get photo count for each person
    for person in people.items:
        person.photo_count = PhotoPerson.query.filter_by(person_id=person.id).count()
    
    return render_template('people.html', people=people)

@main_bp.route('/add_person', methods=['POST'])
@login_required
def add_person():
    """Add a new person"""
    name = request.form.get('name', '').strip()
    nickname = request.form.get('nickname', '').strip()
    relationship = request.form.get('relationship', '').strip()
    birth_year = request.form.get('birth_year', type=int)
    notes = request.form.get('notes', '').strip()
    
    if not name:
        flash('Person name is required', 'error')
        return redirect(url_for('main.people'))
    
    # Check if person already exists for this user
    existing = Person.query.filter_by(user_id=current_user.id, name=name).first()
    if existing:
        flash(f'Person "{name}" already exists', 'error')
        return redirect(url_for('main.people'))
    
    person = Person(
        name=name,
        nickname=nickname,
        relationship=relationship,
        birth_year=birth_year,
        notes=notes,
        user_id=current_user.id
    )
    
    try:
        db.session.add(person)
        db.session.commit()
        flash(f'Added {name} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding person. Please try again.', 'error')
    
    return redirect(url_for('main.people'))

@main_bp.route('/edit_person/<int:person_id>', methods=['POST'])
@login_required
def edit_person(person_id):
    """Edit a person's details"""
    person = Person.query.filter_by(id=person_id, user_id=current_user.id).first_or_404()
    
    person.name = request.form.get('name', '').strip()
    person.nickname = request.form.get('nickname', '').strip()
    person.relationship = request.form.get('relationship', '').strip()
    person.birth_year = request.form.get('birth_year', type=int)
    person.notes = request.form.get('notes', '').strip()
    
    if not person.name:
        flash('Person name is required', 'error')
        return redirect(url_for('main.people'))
    
    try:
        db.session.commit()
        flash(f'Updated {person.name} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating person. Please try again.', 'error')
    
    return redirect(url_for('main.people'))

@main_bp.route('/rename/<int:photo_id>', methods=['POST'])
@login_required
def rename_photo(photo_id):
    """Rename a photo's display name"""
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    
    new_name = request.form.get('new_name', '').strip()
    if not new_name:
        flash('Photo name cannot be empty', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))
    
    # Update the original filename (display name)
    photo.original_filename = new_name
    
    try:
        db.session.commit()
        flash(f'Photo renamed to "{new_name}" successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error renaming photo. Please try again.', 'error')
    
    return redirect(request.referrer or url_for('main.dashboard'))

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload page for photos"""
    if request.method == 'POST':
        # Check if this is an AJAX request (camera capture)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Handle file upload
        if 'file' not in request.files and 'files[]' not in request.files:
            if is_ajax:
                return jsonify({'success': False, 'message': 'No files provided'}), 400
            flash('No files provided', 'error')
            return redirect(url_for('main.upload'))
        
        # Get files (handle both 'file' and 'files[]' for compatibility)
        files = []
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                files.append(file)
        if 'files[]' in request.files:
            files.extend(request.files.getlist('files[]'))
        
        if not files:
            if is_ajax:
                return jsonify({'success': False, 'message': 'No valid files selected'}), 400
            flash('No valid files selected', 'error')
            return redirect(url_for('main.upload'))
        
        uploaded_files = []
        errors = []
        
        for file in files:
            if file and file.filename != '':
                # Import upload logic from photo route
                from photovault.routes.photo import allowed_file
                from werkzeug.utils import secure_filename
                from PIL import Image
                import os, random, string
                
                if allowed_file(file.filename):
                    try:
                        # Generate unique filename
                        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                        filename = f"{random_chars}.{file_ext}" if file_ext else random_chars
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        
                        # Save file
                        file.save(filepath)
                        
                        # Get image dimensions
                        with Image.open(filepath) as img:
                            width, height = img.size
                        
                        # Create database entry
                        photo = Photo(
                            filename=filename,
                            original_filename=secure_filename(file.filename),
                            user_id=current_user.id,
                            file_size=os.path.getsize(filepath),
                            width=width,
                            height=height
                        )
                        db.session.add(photo)
                        uploaded_files.append(filename)
                        
                    except Exception as e:
                        error_msg = f"Error processing {file.filename}: {str(e)}"
                        errors.append(error_msg)
                        if is_ajax:
                            return jsonify({'success': False, 'message': error_msg}), 500
                else:
                    error_msg = f"Invalid file type: {file.filename}"
                    errors.append(error_msg)
                    if is_ajax:
                        return jsonify({'success': False, 'message': error_msg}), 400
        
        try:
            db.session.commit()
            success_message = f'Successfully uploaded {len(uploaded_files)} file(s)!'
            
            # Return appropriate response based on request type
            if is_ajax:
                return jsonify({
                    'success': True, 
                    'message': success_message,
                    'uploaded_files': uploaded_files,
                    'error_count': len(errors)
                })
            else:
                if uploaded_files:
                    flash(success_message, 'success')
                if errors:
                    for error in errors:
                        flash(error, 'error')
                return redirect(url_for('main.dashboard'))
                
        except Exception as e:
            db.session.rollback()
            error_msg = f'Database error: {str(e)}'
            if is_ajax:
                return jsonify({'success': False, 'message': error_msg}), 500
            flash(error_msg, 'error')
            return redirect(url_for('main.upload'))
    
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