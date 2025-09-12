/**
 * PhotoVault Upload & Camera Handler - Clean Implementation
 * Fixes all conflicting implementations and provides unified functionality
 */

class PhotoVaultUploader {
    constructor() {
        // State management
        this.selectedFiles = [];
        this.capturedPhotos = [];
        this.isUploading = false;
        this.currentStream = null;
        this.availableCameras = [];
        this.maxFileSize = 16 * 1024 * 1024; // 16MB
        this.allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        
        this.init();
    }
    
    init() {
        console.log('PhotoVault Uploader: Initializing...');
        this.bindEvents();
        this.initializeCamera().catch(err => {
            console.warn('Camera initialization failed:', err);
        });
    }
    
    bindEvents() {
        // File input events
        const fileInput = document.getElementById('file');
        const uploadForm = document.getElementById('uploadForm');
        const uploadArea = document.getElementById('uploadArea');
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelection(e));
        }
        
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        if (uploadArea) {
            // Click to select files
            uploadArea.addEventListener('click', (e) => {
                if (e.target !== fileInput) {
                    fileInput?.click();
                }
            });
            
            // Drag and drop
            this.setupDragAndDrop(uploadArea);
        }
        
        // Camera events
        this.bindCameraEvents();
    }
    
    bindCameraEvents() {
        const startCameraBtn = document.getElementById('startCameraBtn');
        const captureBtn = document.getElementById('captureBtn');
        const cameraSelect = document.getElementById('cameraSelect');
        
        if (startCameraBtn) {
            startCameraBtn.addEventListener('click', () => this.startCamera());
        }
        
        if (captureBtn) {
            captureBtn.addEventListener('click', () => this.capturePhoto());
        }
        
        if (cameraSelect) {
            cameraSelect.addEventListener('change', () => this.onCameraSelected());
        }
    }
    
    async initializeCamera() {
        if (!navigator.mediaDevices?.getUserMedia) {
            console.log('Camera not supported');
            this.disableCameraUI('Camera not supported in this browser');
            return;
        }
        
        try {
            // Request permission and enumerate devices
            await navigator.mediaDevices.getUserMedia({ video: true });
            await this.enumerateCameras();
        } catch (error) {
            console.error('Camera initialization error:', error);
            this.disableCameraUI('Camera permission denied');
        }
    }
    
    async enumerateCameras() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            this.availableCameras = devices.filter(device => device.kind === 'videoinput');
            const cameraSelect = document.getElementById('cameraSelect');
            
            if (cameraSelect && this.availableCameras.length > 0) {
                cameraSelect.innerHTML = '<option value="">Select Camera...</option>';
                this.availableCameras.forEach((camera, index) => {
                    const option = document.createElement('option');
                    option.value = camera.deviceId;
                    option.textContent = camera.label || `Camera ${index + 1}`;
                    cameraSelect.appendChild(option);
                });
                
                // Auto-select first camera
                if (this.availableCameras.length === 1) {
                    cameraSelect.value = this.availableCameras[0].deviceId;
                }
            } else {
                this.disableCameraUI('No cameras found');
            }
        } catch (error) {
            console.error('Error enumerating cameras:', error);
            this.disableCameraUI('Could not access cameras');
        }
    }
    
    disableCameraUI(message) {
        const cameraSelect = document.getElementById('cameraSelect');
        const startCameraBtn = document.getElementById('startCameraBtn');
        
        if (cameraSelect) {
            cameraSelect.innerHTML = `<option value="">${message}</option>`;
            cameraSelect.disabled = true;
        }
        
        if (startCameraBtn) {
            startCameraBtn.disabled = true;
            startCameraBtn.textContent = message;
        }
    }
    
    onCameraSelected() {
        const startCameraBtn = document.getElementById('startCameraBtn');
        const cameraSelect = document.getElementById('cameraSelect');
        
        if (startCameraBtn && cameraSelect) {
            startCameraBtn.disabled = !cameraSelect.value;
            startCameraBtn.textContent = cameraSelect.value ? 'Start Camera' : 'Select Camera First';
        }
    }
    
    async startCamera() {
        const cameraSelect = document.getElementById('cameraSelect');
        const video = document.getElementById('cameraVideo');
        const captureBtn = document.getElementById('captureBtn');
        const startCameraBtn = document.getElementById('startCameraBtn');
        
        if (!cameraSelect?.value) {
            this.showMessage('Please select a camera', 'warning');
            return;
        }
        
        try {
            // Stop existing stream
            this.stopCamera();
            
            const constraints = {
                video: {
                    deviceId: { exact: cameraSelect.value },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };
            
            this.currentStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            if (video) {
                video.srcObject = this.currentStream;
                video.style.display = 'block';
            }
            
            if (captureBtn) {
                captureBtn.style.display = 'block';
            }
            
            if (startCameraBtn) {
                startCameraBtn.textContent = 'Stop Camera';
                startCameraBtn.onclick = () => this.stopCamera();
            }
            
            this.showMessage('Camera started successfully', 'success');
        } catch (error) {
            console.error('Camera start error:', error);
            this.handleCameraError(error);
        }
    }
    
    stopCamera() {
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }
        
        const video = document.getElementById('cameraVideo');
        const captureBtn = document.getElementById('captureBtn');
        const startCameraBtn = document.getElementById('startCameraBtn');
        
        if (video) {
            video.style.display = 'none';
            video.srcObject = null;
        }
        
        if (captureBtn) {
            captureBtn.style.display = 'none';
        }
        
        if (startCameraBtn) {
            startCameraBtn.textContent = 'Start Camera';
            startCameraBtn.onclick = () => this.startCamera();
        }
    }
    
    handleCameraError(error) {
        let message = 'Camera error occurred';
        
        switch (error.name) {
            case 'NotAllowedError':
                message = 'Camera permission denied. Please allow camera access and try again.';
                break;
            case 'NotFoundError':
                message = 'No camera found. Please check your camera connection.';
                break;
            case 'NotReadableError':
                message = 'Camera is being used by another application.';
                break;
            case 'OverconstrainedError':
                message = 'Camera constraints not supported. Try a different camera.';
                break;
        }
        
        this.showMessage(message, 'error');
    }
    
    capturePhoto() {
        const video = document.getElementById('cameraVideo');
        const canvas = document.getElementById('captureCanvas');
        
        if (!video || !canvas || !this.currentStream) {
            this.showMessage('Camera not ready', 'error');
            return;
        }
        
        const context = canvas.getContext('2d');
        
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        if (canvas.width === 0 || canvas.height === 0) {
            this.showMessage('Could not capture photo - invalid dimensions', 'error');
            return;
        }
        
        // Draw current frame
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Auto-save to database: Upload immediately
        canvas.toBlob((blob) => {
            if (!blob) {
                this.showMessage('Failed to capture photo', 'error');
                return;
            }

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const file = new File([blob], `camera-photo-${timestamp}.jpg`, { type: 'image/jpeg' });

            // Immediately upload single file
            this.uploadSingleFile(file)
                .then(() => {
                    // Add to UI state for visual feedback
                    this.capturedPhotos.push(file);
                    this.selectedFiles.push(file);
                    this.updateFileDisplay();
                    this.showMessage('Photo saved to database!', 'success');
                })
                .catch(error => {
                    console.error('Auto-upload failed:', error);
                    this.showMessage('Failed to save photo to database.', 'error');
                });
        }, 'image/jpeg', 0.9);
    }
    
    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add CSRF token if available
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content 
                       || document.querySelector('input[name="csrf_token"]')?.value;
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return data;
            } else {
                throw new Error(data.message || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }
    
    handleFileSelection(event) {
        const files = Array.from(event.target.files || []);
        
        if (files.length === 0) {
            return;
        }
        
        const validFiles = this.validateFiles(files);
        
        if (validFiles.length === 0) {
            this.showMessage('No valid image files selected', 'warning');
            return;
        }
        
        this.selectedFiles = [...this.selectedFiles, ...validFiles];
        this.updateFileDisplay();
        
        const message = validFiles.length === 1 
            ? `Selected: ${validFiles[0].name}`
            : `Selected ${validFiles.length} files`;
        this.showMessage(message, 'success');
    }
    
    validateFiles(files) {
        return files.filter(file => {
            if (!this.allowedTypes.includes(file.type.toLowerCase())) {
                this.showMessage(`${file.name}: Invalid file type`, 'error');
                return false;
            }
            
            if (file.size > this.maxFileSize) {
                this.showMessage(`${file.name}: File too large (max 16MB)`, 'error');
                return false;
            }
            
            return true;
        });
    }
    
    updateFileDisplay() {
        const fileCount = document.getElementById('fileCount');
        const selectedFilesArea = document.getElementById('selectedFilesArea');
        const uploadBtn = document.getElementById('uploadBtn');
        const clearFilesBtn = document.getElementById('clearFilesBtn');
        
        if (fileCount) {
            fileCount.textContent = this.selectedFiles.length;
        }
        
        if (selectedFilesArea) {
            if (this.selectedFiles.length > 0) {
                selectedFilesArea.style.display = 'block';
                this.renderFilePreview();
            } else {
                selectedFilesArea.style.display = 'none';
            }
        }
        
        if (uploadBtn) {
            uploadBtn.disabled = this.selectedFiles.length === 0 || this.isUploading;
        }
        
        if (clearFilesBtn) {
            clearFilesBtn.disabled = this.selectedFiles.length === 0;
        }
    }
    
    renderFilePreview() {
        const container = document.getElementById('filePreviewContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item d-flex align-items-center justify-content-between p-2 border rounded mb-2';
            
            fileItem.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-image text-primary me-2"></i>
                    <div>
                        <div class="fw-semibold">${file.name}</div>
                        <small class="text-muted">${this.formatFileSize(file.size)}</small>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="photoVaultUploader.removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            container.appendChild(fileItem);
        });
    }
    
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileDisplay();
        this.showMessage('File removed', 'info');
    }
    
    clearFiles() {
        this.selectedFiles = [];
        this.updateFileDisplay();
        this.showMessage('All files cleared', 'info');
        
        // Clear file input
        const fileInput = document.getElementById('file');
        if (fileInput) {
            fileInput.value = '';
        }
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        if (this.selectedFiles.length === 0) {
            this.showMessage('Please select files to upload', 'warning');
            return;
        }
        
        if (this.isUploading) {
            return;
        }
        
        this.isUploading = true;
        this.showProgress();
        
        try {
            const formData = new FormData();
            
            // Add all selected files
            this.selectedFiles.forEach(file => {
                formData.append('file', file);
            });
            
            // Add CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content 
                           || document.querySelector('input[name="csrf_token"]')?.value;
            if (csrfToken) {
                formData.append('csrf_token', csrfToken);
            }
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.showMessage(data.message || 'Upload successful!', 'success');
                this.selectedFiles = [];
                this.updateFileDisplay();
                
                // Clear file input
                const fileInput = document.getElementById('file');
                if (fileInput) {
                    fileInput.value = '';
                }
                
                // Redirect to dashboard after delay
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                throw new Error(data.message || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showMessage(error.message || 'Upload failed. Please try again.', 'error');
        } finally {
            this.isUploading = false;
            this.hideProgress();
        }
    }
    
    setupDragAndDrop(uploadArea) {
        const events = ['dragenter', 'dragover', 'dragleave', 'drop'];
        
        events.forEach(eventName => {
            uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        uploadArea.addEventListener('dragenter', () => {
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            if (!uploadArea.contains(e.relatedTarget)) {
                uploadArea.classList.remove('drag-over');
            }
        });
        
        uploadArea.addEventListener('drop', (e) => {
            uploadArea.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                const validFiles = this.validateFiles(files);
                if (validFiles.length > 0) {
                    this.selectedFiles = [...this.selectedFiles, ...validFiles];
                    this.updateFileDisplay();
                    this.showMessage(`Added ${validFiles.length} files`, 'success');
                }
            }
        });
    }
    
    showProgress() {
        const uploadProgress = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (uploadProgress) {
            uploadProgress.style.display = 'block';
        }
        
        if (progressBar) {
            progressBar.style.width = '0%';
            progressBar.setAttribute('aria-valuenow', '0');
        }
        
        if (progressText) {
            progressText.textContent = 'Uploading...';
        }
        
        if (uploadBtn) {
            uploadBtn.disabled = true;
        }
        
        // Simulate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress > 90) progress = 90;
            
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress.toString());
            }
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 500);
    }
    
    hideProgress() {
        const uploadProgress = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (uploadProgress) {
            uploadProgress.style.display = 'none';
        }
        
        if (progressBar) {
            progressBar.style.width = '100%';
            progressBar.setAttribute('aria-valuenow', '100');
        }
        
        if (uploadBtn) {
            uploadBtn.disabled = this.selectedFiles.length === 0;
        }
    }
    
    showMessage(message, type = 'info') {
        const container = document.getElementById('uploadMessages');
        if (!container) {
            console.log(`[${type.toUpperCase()}] ${message}`);
            return;
        }
        
        const alertClass = type === 'error' ? 'danger' : type;
        const alert = document.createElement('div');
        alert.className = `alert alert-${alertClass} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(alert);
        
        // Auto-dismiss after 5 seconds for success/info messages
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.photoVaultUploader = new PhotoVaultUploader();
});