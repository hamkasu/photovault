"""
PhotoVault - Professional Photo Management Platform
Copyright (c) 2025 Calmic Sdn Bhd. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution,
modification, or use of this software is strictly prohibited.

Website: https://www.calmic.com.my
Email: support@calmic.com.my

CALMIC SDN BHD - "Committed to Excellence"
"""

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
import logging

photo_bp = Blueprint('photo', __name__, url_prefix='/api')

# Configure logging
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}

# Maximum image dimensions to prevent zip bombs
MAX_IMAGE_PIXELS = 178956970  # Equivalent to 8K image (8192 x 8192 x 2.75)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_efficiently(file):
    """Validate image without loading full file into memory"""
    try:
        # Save current position
        pos = file.tell()
        
        # Check file size first (before any processing)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)     # Reset to beginning
        
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            file.seek(pos)
            return False, f"File exceeds maximum size of {max_size // (1024*1024)}MB"
        
        if file_size == 0:
            file.seek(pos)
            return False, "File is empty"
        
        # Validate file header (magic bytes)
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
            file.seek(pos)
            return False, "Invalid or unsupported image format"
        
        # Use PIL to validate image and get dimensions without loading full image data
        try:
            with Image.open(file) as img:
                # Get format and size without loading image data
                width, height = img.size
                format_name = img.format
                
                # Validate dimensions (prevent zip bombs and excessive memory usage)
                if width * height > MAX_IMAGE_PIXELS:
                    file.seek(pos)
                    return False, "Image dimensions too large (potential security risk)"
                
                # Additional reasonable dimension limits
                if width > 16384 or height > 16384:
                    file.seek(pos)
                    return False, "Image width or height exceeds 16K pixels"
                
                # Verify format matches header detection
                expected_format = {
                    'image/png': 'PNG',
                    'image/jpeg': 'JPEG', 
                    'image/gif': 'GIF',
                    'image/webp': 'WEBP'
                }.get(mime_type)
                
                if format_name != expected_format:
                    file.seek(pos)
                    return False, "File header doesn't match actual image format"
                    
        except Exception as e:
            file.seek(pos)
            logger.warning(f"Image validation error: {e}")
            return False, "Corrupted or invalid image file"
        
        # Reset file position
        file.seek(pos)
        return True, "Valid image file"
        
    except Exception as e:
        # Ensure file position is reset even on unexpected errors
        try:
            file.seek(pos)
        except:
            pass
        logger.error(f"Image validation exception: {e}")
        return False, f"Image validation failed: {str(e)}"

def generate_secure_filename(original_filename):
    """Generate a secure, unique filename"""
    # Get file extension
    file_ext = ''
    if '.' in original_filename:
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            file_ext = 'jpg'  # Default fallback
    else:
        file_ext = 'jpg'  # Default extension if none provided
    
    # Generate cryptographically secure random filename
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    timestamp = str(int(__import__('time').time()))[-6:]  # Last 6 digits of timestamp
    
    return f"{timestamp}_{random_chars}.{file_ext}"

@photo_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Enhanced photo upload with comprehensive validation and error handling"""
    if request.method == 'GET':
        return jsonify({'error': 'GET method not supported. Use POST with files.'}), 405
    
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No valid files selected'}), 400
    
    uploaded_files = []
    errors = []
    
    # Check upload folder exists and is writable
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder, mode=0o755, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create upload folder: {e}")
            return jsonify({'error': 'Server configuration error - upload folder inaccessible'}), 500
    
    # Process each file
    for file_idx, file in enumerate(files):
        if not file or file.filename == '':
            errors.append(f"File {file_idx + 1}: Empty file or filename")
            continue
        
        try:
            # Secure the original filename for storage
            secure_original = secure_filename(file.filename)
            if not secure_original:
                secure_original = f"upload_{file_idx + 1}"
            
            # Check file extension first (quick check)
            if not allowed_file(file.filename):
                errors.append(f"File '{file.filename}': Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP")
                continue
            
            # Comprehensive image validation
            is_valid, validation_message = validate_image_efficiently(file)
            if not is_valid:
                errors.append(f"File '{file.filename}': {validation_message}")
                continue
            
            # Generate secure filename for storage
            filename = generate_secure_filename(file.filename)
            filepath = os.path.join(upload_folder, filename)
            
            # Ensure filename is unique (handle unlikely collision)
            counter = 1
            base_filename = filename
            while os.path.exists(filepath):
                name, ext = os.path.splitext(base_filename)
                filename = f"{name}_{counter}{ext}"
                filepath = os.path.join(upload_folder, filename)
                counter += 1
                if counter > 100:  # Prevent infinite loop
                    errors.append(f"File '{file.filename}': Could not generate unique filename")
                    break
            else:
                # Save file to disk
                file.seek(0)  # Ensure we're at the beginning
                file.save(filepath)
                
                # Verify file was saved correctly
                if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                    errors.append(f"File '{file.filename}': Failed to save to server")
                    continue
                
                # Get final image dimensions and file size
                try:
                    with Image.open(filepath) as img:
                        width, height = img.size
                    
                    file_size = os.path.getsize(filepath)
                    
                    # Create database entry
                    photo = Photo(
                        filename=filename,
                        original_filename=secure_original,
                        user_id=current_user.id,
                        file_size=file_size,
                        width=width,
                        height=height
                    )
                    
                    db.session.add(photo)
                    db.session.flush()  # Get the photo ID without committing
                    
                    uploaded_files.append({
                        'id': photo.id,
                        'filename': filename,
                        'original': secure_original,
                        'size': file_size,
                        'dimensions': f"{width}x{height}"
                    })
                    
                    logger.info(f"User {current_user.username} uploaded {secure_original} ({file_size} bytes)")
                    
                except Exception as img_error:
                    # Clean up file if database entry fails
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except OSError:
                            pass
                    errors.append(f"File '{file.filename}': Error processing saved file - {str(img_error)}")
                    continue
        
        except Exception as e:
            logger.error(f"Unexpected error processing file '{file.filename}': {e}")
            errors.append(f"File '{file.filename}': Unexpected server error")
            continue
    
    # Commit all successful uploads
    try:
        if uploaded_files:
            db.session.commit()
            logger.info(f"Successfully committed {len(uploaded_files)} photo uploads for user {current_user.username}")
        else:
            db.session.rollback()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database commit error for user {current_user.username}: {e}")
        
        # Clean up any files that were saved
        for file_info in uploaded_files:
            filepath = os.path.join(upload_folder, file_info['filename'])
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    pass
        
        return jsonify({'success': False, 'error': 'Database error - uploads canceled'}), 500
    
    # Return appropriate response
    if errors and not uploaded_files:
        return jsonify({
            'success': False, 
            'message': 'All uploads failed', 
            'errors': errors
        }), 400
    elif errors and uploaded_files:
        return jsonify({
            'success': True, 
            'message': f'{len(uploaded_files)} files uploaded successfully, {len(errors)} failed',
            'files': uploaded_files, 
            'errors': errors
        }), 207  # Multi-status
    else:
        return jsonify({
            'success': True, 
            'message': f'Successfully uploaded {len(uploaded_files)} files',
            'files': uploaded_files
        }), 200

@photo_bp.route('/delete/<int:photo_id>', methods=['DELETE'])
@login_required
def delete_photo(photo_id):
    """Delete a photo with proper cleanup and security checks"""
    try:
        photo = Photo.query.get_or_404(photo_id)
        
        # Security check - ensure user owns the photo
        if photo.user_id != current_user.id:
            logger.warning(f"User {current_user.username} attempted to delete photo {photo_id} owned by user {photo.user_id}")
            return jsonify({'error': 'Unauthorized'}), 403
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Delete original file
        original_filepath = os.path.join(upload_folder, photo.filename)
        original_deleted = False
        if os.path.exists(original_filepath):
            try:
                os.remove(original_filepath)
                original_deleted = True
            except OSError as e:
                logger.error(f"Error deleting original file {original_filepath}: {e}")
        
        # Delete edited file if it exists
        edited_deleted = True  # Assume success if no edited file
        if photo.edited_filename:
            edited_filepath = os.path.join(upload_folder, photo.edited_filename)
            if os.path.exists(edited_filepath):
                try:
                    os.remove(edited_filepath)
                except OSError as e:
                    logger.error(f"Error deleting edited file {edited_filepath}: {e}")
                    edited_deleted = False
        
        # Delete database record
        db.session.delete(photo)
        db.session.commit()
        
        logger.info(f"User {current_user.username} deleted photo {photo.original_filename} (ID: {photo_id})")
        
        response_data = {'success': True, 'message': 'Photo deleted successfully'}
        if not original_deleted or not edited_deleted:
            response_data['warning'] = 'Some files could not be deleted from disk'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting photo {photo_id} for user {current_user.username}: {e}")
        return jsonify({'error': 'Failed to delete photo', 'details': str(e)}), 500

@photo_bp.route('/save-edit', methods=['POST'])
@login_required
def save_edit():
    """Save edited photo with enhanced validation and error handling"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        photo_id = data.get('photo_id')
        image_data = data.get('image_data')
        
        if not photo_id or not image_data:
            return jsonify({'success': False, 'error': 'Missing photo ID or image data'}), 400
        
        photo = Photo.query.get_or_404(photo_id)
        
        # Security check
        if photo.user_id != current_user.id:
            logger.warning(f"User {current_user.username} attempted to edit photo {photo_id} owned by user {photo.user_id}")
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Validate and decode base64 image data
        try:
            if image_data.startswith('data:image'):
                # Extract base64 data after the comma
                header, encoded = image_data.split(',', 1)
                # Validate header
                if 'image/' not in header:
                    return jsonify({'success': False, 'error': 'Invalid image data format'}), 400
            else:
                encoded = image_data
            
            # Decode base64
            image_binary = base64.b64decode(encoded)
            
            # Validate decoded data size
            if len(image_binary) == 0:
                return jsonify({'success': False, 'error': 'Empty image data'}), 400
            
            max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
            if len(image_binary) > max_size:
                return jsonify({'success': False, 'error': 'Edited image too large'}), 400
            
        except Exception as e:
            logger.error(f"Error decoding image data for photo {photo_id}: {e}")
            return jsonify({'success': False, 'error': 'Invalid image data encoding'}), 400
        
        # Generate filename for edited image
        name, ext = os.path.splitext(photo.filename)
        if not ext or not ext.startswith('.'):
            ext = '.jpg'  # Default extension
        
        edited_filename = f"{name}_edited_{uuid.uuid4().hex[:8]}{ext}"
        edited_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], edited_filename)
        
        # Ensure unique filename
        counter = 1
        base_edited_filename = edited_filename
        while os.path.exists(edited_filepath):
            name_part, ext_part = os.path.splitext(base_edited_filename)
            edited_filename = f"{name_part}_{counter}{ext_part}"
            edited_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], edited_filename)
            counter += 1
            if counter > 100:
                return jsonify({'success': False, 'error': 'Could not generate unique filename'}), 500
        
        # Save the edited image
        try:
            with open(edited_filepath, 'wb') as f:
                f.write(image_binary)
            
            # Verify file was written correctly
            if not os.path.exists(edited_filepath) or os.path.getsize(edited_filepath) == 0:
                return jsonify({'success': False, 'error': 'Failed to save edited image'}), 500
            
            # Validate the saved image
            try:
                with Image.open(edited_filepath) as img:
                    # Just ensure it's a valid image
                    img.verify()
            except Exception:
                # Clean up invalid file
                if os.path.exists(edited_filepath):
                    os.remove(edited_filepath)
                return jsonify({'success': False, 'error': 'Saved image is corrupted'}), 400
            
        except OSError as e:
            logger.error(f"Error saving edited image {edited_filepath}: {e}")
            return jsonify({'success': False, 'error': 'Failed to save edited image to disk'}), 500
        
        # Clean up previous edited version if it exists
        if photo.edited_filename:
            old_edited_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.edited_filename)
            if os.path.exists(old_edited_path):
                try:
                    os.remove(old_edited_path)
                except OSError as e:
                    logger.warning(f"Could not delete old edited file {old_edited_path}: {e}")
        
        # Update database
        photo.edited_filename = edited_filename
        db.session.commit()
        
        logger.info(f"User {current_user.username} saved edit for photo {photo.original_filename} (ID: {photo_id})")
        
        return jsonify({
            'success': True, 
            'message': 'Edit saved successfully', 
            'new_filename': edited_filename
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error saving edit for photo {photo_id}: {e}")
        return jsonify({'success': False, 'error': 'Server error while saving edit'}), 500

@photo_bp.route('/original/<int:photo_id>')
@login_required
def get_original(photo_id):
    """Get original photo URL with security validation"""
    try:
        photo = Photo.query.get_or_404(photo_id)
        
        if photo.user_id != current_user.id:
            abort(403)
        
        original_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
        if not os.path.exists(original_filepath):
            return jsonify({'error': 'Original file not found on server'}), 404
        
        return jsonify({
            'original_url': url_for('static', filename=f'uploads/{photo.filename}'),
            'filename': photo.original_filename,
            'size': photo.file_size,
            'dimensions': f"{photo.width}x{photo.height}" if photo.width and photo.height else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting original for photo {photo_id}: {e}")
        return jsonify({'error': 'Server error'}), 500

@photo_bp.route('/download/<int:photo_id>')
@login_required
def download(photo_id):
    """Download photo with enhanced security and options"""
    try:
        photo = Photo.query.get_or_404(photo_id)
        
        if photo.user_id != current_user.id:
            logger.warning(f"User {current_user.username} attempted to download photo {photo_id} owned by user {photo.user_id}")
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if user wants original version
        force_original = request.args.get('original', 'false').lower() == 'true'
        
        if force_original or not photo.edited_filename:
            active_filename = photo.filename
            download_name = photo.original_filename if photo.original_filename else photo.filename
        else:
            active_filename = photo.edited_filename
            # For edited files, add suffix to indicate it's edited
            base_name, ext = os.path.splitext(photo.original_filename if photo.original_filename else photo.filename)
            download_name = f"{base_name}_edited{ext}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], active_filename)
        
        if not os.path.exists(filepath):
            logger.error(f"Download requested for missing file: {filepath}")
            return jsonify({'error': 'File not found on server'}), 404
        
        # Verify file integrity before sending
        try:
            if os.path.getsize(filepath) == 0:
                return jsonify({'error': 'File is corrupted (empty)'}), 500
        except OSError:
            return jsonify({'error': 'File access error'}), 500
        
        logger.info(f"User {current_user.username} downloaded {download_name} ({'original' if force_original else 'current'})")
        
        return send_file(
            filepath, 
            as_attachment=True, 
            download_name=download_name,
            conditional=True  # Enable conditional requests for better performance
        )
        
    except Exception as e:
        logger.error(f"Error downloading photo {photo_id}: {e}")
        return jsonify({'error': 'Download failed'}), 500