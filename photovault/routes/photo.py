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
# --- Added imports for 6-char filename ---
import random
import string

# --- Add this import to get the limiter ---
from photovault import limiter
# --- End Add import ---

# --- Added imports for 6-char filename ---
import random
import string
# --- End Added imports ---

# --- End Added imports ---
photo_bp = Blueprint('photo', __name__, url_prefix='/api')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# Define allowed MIME types for stricter validation
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@photo_bp.route('/upload', methods=['POST'])
@login_required
@limiter.limit("10 per minute") # Add this decorator

def upload():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    files = request.files.getlist('files[]')
    uploaded_files = []
    errors = []
    # --- Get the configured max size for explicit server-side checking ---
    max_size = current_app.config['MAX_CONTENT_LENGTH']
    # ---
    for file in files:
        if file and file.filename != '' and allowed_file(file.filename):
            try:
                # --- Add explicit server-side file size validation ---
                if file.content_length > max_size:
                    error_msg = f"File {file.filename} exceeds maximum size of {max_size / (1024*1024):.0f}MB."
                    print(f"Upload Rejected: {error_msg}")
                    errors.append(error_msg)
                    continue # Skip this file, continue with others
                # --- End file size validation ---
                # --- Enhanced Security: Validate MIME type by content, not just extension ---
                # Read the first few bytes to determine the actual MIME type
                file.seek(0) # Ensure we're at the start of the file
                header = file.read(512) # Read first 512 bytes
                file.seek(0) # Reset file pointer for saving
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
                    print(f"Security Warning: {error_msg}")
                    errors.append(error_msg)
                    continue
                # --- End Enhanced Security ---
                # --- Generate unique 6-character random filename ---
                # Get file extension securely
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                # Generate 6 random alphanumeric characters
                random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                # Combine random chars with extension (ensure dot is added)
                filename = f"{random_chars}.{file_ext}" if file_ext else random_chars
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                # --- End Generate unique filename ---
                # Save file
                file.save(filepath)
                # Get image dimensions (this also validates it's a real image)
                with Image.open(filepath) as img:
                    width, height = img.size
                # Create database entry
                # Ensure the Photo model has the edited_filename column
                photo = Photo(
                    filename=filename, # This now stores the original/random name
                    original_filename=secure_filename(file.filename),
                    user_id=current_user.id,
                    file_size=os.path.getsize(filepath),
                    width=width,
                    height=height
                    # edited_filename is NULL by default
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
                print(f"Upload Error: {error_msg}")
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
    # Delete files: original and potentially edited
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
    # Delete database entry
    db.session.delete(photo)
    db.session.commit()
    return jsonify({'success': True})
# --- Modified save_edit function ---
@photo_bp.route('/save-edit', methods=['POST'])
@login_required
def save_edit():
    data = request.json
    photo_id = data.get('photo_id')
    image_data = data.get('image_data')
    # --- FIX: Complete the validation check ---
    if not photo_id or not image_data:
        return jsonify({'success': False, 'error': 'Missing photo ID or image data'}), 400
    # --- END FIX ---
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    try:
        # Decode base64 image
        # Assumes data URL format: data:image/jpeg;base64,...
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        image_binary = base64.b64decode(image_data)
        # --- Generate new filename for edited image ---
        name, ext = os.path.splitext(photo.filename)
        # Ensure extension starts with a dot, default to .jpg if none found or invalid
        if not ext or not ext.startswith('.'):
            # A more robust way would be to detect MIME type, but this is a simple fallback
            ext = '.jpg'
        edited_filename = f"{name}_edited_{uuid.uuid4().hex}{ext}"
        edited_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], edited_filename)
        # --- End Generate new filename ---
        # Save the edited image as a new file
        with open(edited_filepath, 'wb') as f:
            f.write(image_binary)
        # --- Update database to store the edited filename ---
        photo.edited_filename = edited_filename # Store the edited filename
        db.session.commit()
        # --- End Update database ---
    except Exception as e:
        db.session.rollback()
        print(f"Error saving edited image for photo {photo_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to save edited image'}), 500
    return jsonify({'success': True, 'message': 'Edit saved successfully', 'new_filename': edited_filename})
# --- End Modified save_edit function ---
# --- New route to get the original image URL ---
@photo_bp.route('/original/<int:photo_id>')
@login_required
def get_original(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        abort(403) # Or return JSON error
    # The original filename is stored in photo.filename
    original_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
    if not os.path.exists(original_filepath):
        abort(404) # Or return JSON error
    # Return the URL to the original file so the frontend can use it
    # We return JSON, the frontend can use this URL in an <img> tag
    # e.g., <img src="{{ url_for('photo.get_original', photo_id=photo.id) }}">
    return jsonify({'original_url': url_for('static', filename=f'uploads/{photo.filename}')})
# --- End New route ---
@photo_bp.route('/download/<int:photo_id>')
@login_required
def download(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    # Decide which file to download: original or edited
    # Download the active version (edited if exists, otherwise original)
    active_filename = photo.edited_filename if photo.edited_filename else photo.filename
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], active_filename)
    # Use the original filename for download, or the active one if original is not set
    download_name = photo.original_filename if photo.original_filename else active_filename
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found on server'}), 404
    return send_file(filepath, as_attachment=True, download_name=download_name)
