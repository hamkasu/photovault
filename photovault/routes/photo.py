# photovault/routes/photo.py
from flask import Blueprint, request, jsonify, current_app, send_file, url_for, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from photovault import db
from photovault.models import Photo
from PIL import Image
import os
import uuid
import base64
import random
import string

photo_bp = Blueprint('photo', __name__, url_prefix='/api')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@photo_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    uploaded_files = []
    errors = []
    max_size = current_app.config['MAX_CONTENT_LENGTH']
    
    for file in files:
        if file and file.filename != '' and allowed_file(file.filename):
            try:
                # File size validation
                if file.content_length and file.content_length > max_size:
                    error_msg = f"File {file.filename} exceeds maximum size of {max_size / (1024*1024):.0f}MB."
                    errors.append(error_msg)
                    continue
                
                # MIME type validation
                file.seek(0)
                header = file.read(512)
                file.seek(0)
                
                mime_type = None
                if header.startswith(b'\x89PNG\r\n\x1a\n'):
                    mime_type = 'image/png'
                elif header.startswith(b'\xff\xd8\xff'):
                    mime_type = 'image/jpeg'
                elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
                    mime_type = 'image/gif'
                elif header.startswith(b'RIFF') and header[8:12] == b'WEBP':
                    mime_type = 'image/webp'
                
                if mime_type not in ALLOWED_MIME_TYPES:
                    error_msg = f"File {file.filename} is not a valid image type."
                    errors.append(error_msg)
                    continue
                
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
                db.session.commit()
                
                uploaded_files.append({
                    'id': photo.id,
                    'filename': filename,
                    'original': photo.original_filename
                })
                
            except Exception as e:
                db.session.rollback()
                error_msg = f"Error processing file {file.filename}: {str(e)}"
                errors.append(error_msg)
        else:
            errors.append(f"Invalid file or empty filename for upload.")
    
    if errors and not uploaded_files:
        return jsonify({'success': False, 'message': 'All uploads failed.', 'errors': errors}), 400
    elif errors:
        return jsonify({'success': True, 'message': 'Some files uploaded.', 'files': uploaded_files, 'errors': errors}), 207
    else:
        return jsonify({'success': True, 'files': uploaded_files})

@photo_bp.route('/delete/<int:photo_id>', methods=['DELETE'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete files
    original_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
    if os.path.exists(original_filepath):
        try:
            os.remove(original_filepath)
        except OSError as e:
            print(f"Error deleting original file {original_filepath}: {e}")
    
    if photo.edited_filename:
        edited_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.edited_filename)
        if os.path.exists(edited_filepath):
            try:
                os.remove(edited_filepath)
            except OSError as e:
                print(f"Error deleting edited file {edited_filepath}: {e}")
    
    db.session.delete(photo)
    db.session.commit()
    return jsonify({'success': True})

@photo_bp.route('/save-edit', methods=['POST'])
@login_required
def save_edit():
    data = request.json
    photo_id = data.get('photo_id')
    image_data = data.get('image_data')
    
    if not photo_id or not image_data:
        return jsonify({'success': False, 'error': 'Missing photo ID or image data'}), 400
    
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        # Decode base64 image
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        image_binary = base64.b64decode(image_data)
        
        # Generate filename for edited image
        name, ext = os.path.splitext(photo.filename)
        if not ext or not ext.startswith('.'):
            ext = '.jpg'
        edited_filename = f"{name}_edited_{uuid.uuid4().hex}{ext}"
        edited_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], edited_filename)
        
        # Save the edited image
        with open(edited_filepath, 'wb') as f:
            f.write(image_binary)
        
        # Update database
        photo.edited_filename = edited_filename
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving edited image for photo {photo_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to save edited image'}), 500
    
    return jsonify({'success': True, 'message': 'Edit saved successfully', 'new_filename': edited_filename})

@photo_bp.route('/original/<int:photo_id>')
@login_required
def get_original(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        abort(403)
    
    original_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
    if not os.path.exists(original_filepath):
        abort(404)
    
    return jsonify({'original_url': url_for('static', filename=f'uploads/{photo.filename}')})

@photo_bp.route('/download/<int:photo_id>')
@login_required
def download(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if user wants original version
    force_original = request.args.get('original', 'false').lower() == 'true'
    
    if force_original:
        active_filename = photo.filename
        download_name = photo.original_filename if photo.original_filename else photo.filename
    else:
        active_filename = photo.edited_filename if photo.edited_filename else photo.filename
        download_name = photo.original_filename if photo.original_filename else active_filename
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], active_filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found on server'}), 404
    
    return send_file(filepath, as_attachment=True, download_name=download_name)