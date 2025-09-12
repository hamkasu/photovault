/**
<<<<<<< HEAD
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

        // ✅ AUTO-SAVE TO DATABASE: Upload immediately
        canvas.toBlob((blob) => {
            if (!blob) {
                this.showMessage('Failed to capture photo', 'error');
                return;
            }

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const file = new File([blob], `camera-photo-${timestamp}.jpg`, { type: 'image/jpeg' });

            // ✅ Immediately upload single file
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
        
        // ✅ Add CSRF token (correctly placed inside method)
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content 
                       || document.querySelector('input[name="csrf_token"]')?.value;
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        
        // ✅ Add single file
        formData.append('files[]', file); // Backend expects array even for single file

        this.showProgress();
        this.showMessage('Saving photo to database...', 'info');

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
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
        } finally {
            this.hideProgress();
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
=======
 * PhotoVault Upload Handler - Prevents Double Dialog Issue
 * Fixed version that handles single file dialog properly
 */

class PhotoVaultUploader {
    constructor() {
        // DOM Elements
        this.fileInput = document.getElementById('fileInput');
        this.uploadArea = document.getElementById('uploadArea');
        this.selectPhotosBtn = document.getElementById('selectPhotosBtn');
        this.uploadForm = document.getElementById('uploadForm');
        this.selectedFilesArea = document.getElementById('selectedFilesArea');
        this.filePreviewContainer = document.getElementById('filePreviewContainer');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.clearFilesBtn = document.getElementById('clearFilesBtn');
        this.uploadProgress = document.getElementById('uploadProgress');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.uploadMessages = document.getElementById('uploadMessages');
        this.fileCount = document.getElementById('fileCount');
        
        // State Management
        this.selectedFiles = [];
        this.isUploading = false;
        this.dialogState = 'closed';
        this.maxFileSize = 16 * 1024 * 1024; // 16MB
        this.allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        
        // Initialize only once
        this.init();
    }
    
    init() {
        console.log('PhotoVault Uploader: Initializing...');
        
        // Remove any existing event listeners first
        this.removeAllEventListeners();
        
        // Bind events with prevention of multiple triggers
        this.bindEvents();
        
        console.log('PhotoVault Uploader: Ready');
    }
    
    removeAllEventListeners() {
        // Clone elements to remove ALL event listeners
        if (this.selectPhotosBtn) {
            const newBtn = this.selectPhotosBtn.cloneNode(true);
            this.selectPhotosBtn.parentNode.replaceChild(newBtn, this.selectPhotosBtn);
            this.selectPhotosBtn = document.getElementById('selectPhotosBtn');
        }
    }
    
    bindEvents() {
        // PRIMARY: Button click to open file dialog
        this.selectPhotosBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.openFileDialog('button_click');
        });
        
        // SECONDARY: Upload area click (but not on button)
        this.uploadArea?.addEventListener('click', (e) => {
            if (!this.selectPhotosBtn?.contains(e.target)) {
                e.preventDefault();
                e.stopPropagation();
                this.openFileDialog('area_click');
            }
        });
        
        // File input change event
        this.fileInput?.addEventListener('change', (e) => {
            this.handleFileSelection(e);
        });
        
        // Drag and Drop
        this.setupDragAndDrop();
        
        // Form submission
        this.uploadForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUpload();
        });
        
        // Clear files button
        this.clearFilesBtn?.addEventListener('click', () => {
            this.clearSelection();
        });
    }
    
    openFileDialog(source) {
        // CRITICAL: Prevent multiple dialogs
        if (this.dialogState === 'opening' || this.dialogState === 'open') {
            console.log(`PhotoVault: Dialog already ${this.dialogState}, ignoring ${source}`);
            return;
        }
        
        if (this.isUploading) {
            console.log('PhotoVault: Upload in progress, ignoring dialog request');
            return;
        }
        
        console.log(`PhotoVault: Opening file dialog from ${source}`);
        
        // Set state to prevent multiple opens
        this.dialogState = 'opening';
        this.fileInput.dataset.dialogState = 'opening';
        
        // Reset state after dialog interaction
        const resetDialogState = () => {
            setTimeout(() => {
                this.dialogState = 'closed';
                this.fileInput.dataset.dialogState = 'closed';
            }, 500);
        };
        
        // Listen for focus return (dialog closed)
        const focusHandler = () => {
            resetDialogState();
            window.removeEventListener('focus', focusHandler);
        };
        window.addEventListener('focus', focusHandler);
        
        // Also reset after a timeout as backup
        setTimeout(resetDialogState, 2000);
        
        // Trigger file input
        this.fileInput.click();
        this.dialogState = 'open';
    }
    
    handleFileSelection(e) {
        const files = Array.from(e.target.files || []);
        console.log(`PhotoVault: ${files.length} files selected`);
        
        if (files.length === 0) {
            this.clearSelection();
            return;
        }
        
        // Validate files
        const validFiles = this.validateFiles(files);
        
        if (validFiles.length === 0) {
            this.showMessage('No valid image files selected', 'warning');
            this.clearSelection();
            return;
        }
        
        // Store selected files
        this.selectedFiles = validFiles;
        
        // Update UI
        this.displayFilePreview();
        this.updateFileCount();
        this.selectedFilesArea.style.display = 'block';
        
        this.showMessage(`${validFiles.length} files ready for upload`, 'success');
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
    }
    
    validateFiles(files) {
        const validFiles = [];
        const errors = [];
<<<<<<< HEAD
        files.forEach(file => {
            if (!this.allowedTypes.includes(file.type.toLowerCase())) {
                errors.push(`${file.name}: Invalid file type`);
                return;
            }
=======
        
        files.forEach(file => {
            // Check file type
            if (!this.allowedTypes.includes(file.type)) {
                errors.push(`${file.name}: Invalid file type`);
                return;
            }
            
            // Check file size
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
            if (file.size > this.maxFileSize) {
                errors.push(`${file.name}: File too large (max 16MB)`);
                return;
            }
<<<<<<< HEAD
            validFiles.push(file);
        });
        if (errors.length > 0) {
            this.showMessage(errors.join('<br>'), 'warning');
        }
        return validFiles;
    }
    
    updateFileDisplay() {
        const uploadStatus = document.getElementById('uploadStatus');
        const filePreviewsContainer = document.getElementById('filePreviews');
        const uploadBtn = document.getElementById('uploadBtn');

        if (this.selectedFiles.length === 0) {
            if (uploadStatus) {
                uploadStatus.innerHTML = `
                    <i class="bi bi-cloud-upload" style="font-size: 3rem; color: #6c757d;"></i>
                    <h5 class="mt-3">Choose Photos to Upload</h5>
                    <p class="text-muted">Drag and drop files here, or click to select</p>
                `;
            }
            if (filePreviewsContainer) {
                filePreviewsContainer.innerHTML = ''; // Clear any existing previews
            }
            if (uploadBtn) uploadBtn.disabled = true;
            return;
        }

        const fileCount = this.selectedFiles.length;
        const capturedCount = this.capturedPhotos.length;
        let statusText = `${fileCount} file${fileCount > 1 ? 's' : ''} selected`;
        if (capturedCount > 0) {
            statusText += ` (${capturedCount} captured from camera)`;
        }

        // Update main status text
        if (uploadStatus) {
            uploadStatus.innerHTML = `
                <i class="bi bi-file-image text-success" style="font-size: 3rem;"></i>
                <h5 class="mt-3 text-success">${statusText}</h5>
                <small class="text-success">Ready to upload</small>
            `;
        }

        // Clear and rebuild preview thumbnails
        if (filePreviewsContainer) {
            filePreviewsContainer.innerHTML = '';
            this.selectedFiles.forEach(file => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.alt = file.name;
                    img.style.width = '80px';
                    img.style.height = '80px';
                    img.style.objectFit = 'cover';
                    img.style.borderRadius = '4px';
                    img.style.border = '1px solid #dee2e6';
                    img.title = file.name;
                    filePreviewsContainer.appendChild(img);
                };
                reader.readAsDataURL(file);
            });
        }

        if (uploadBtn) uploadBtn.disabled = false;
    }
    
    setupDragAndDrop(uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, (e) => {
=======
            
            validFiles.push(file);
        });
        
        // Show validation errors
        if (errors.length > 0) {
            this.showMessage(`Some files were rejected:<br>${errors.join('<br>')}`, 'warning');
        }
        
        return validFiles;
    }
    
    displayFilePreview() {
        this.filePreviewContainer.innerHTML = '';
        
        this.selectedFiles.forEach((file, index) => {
            const previewItem = document.createElement('div');
            previewItem.className = 'file-preview-item';
            
            // Create image preview
            const img = document.createElement('img');
            img.className = 'file-preview-img';
            img.alt = file.name;
            
            // Create file reader for preview
            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
            
            // File info
            const fileName = document.createElement('div');
            fileName.className = 'file-preview-name';
            fileName.textContent = file.name.length > 20 ? 
                file.name.substring(0, 17) + '...' : file.name;
            
            const fileSize = document.createElement('div');
            fileSize.className = 'file-preview-size';
            fileSize.textContent = this.formatFileSize(file.size);
            
            // Remove button
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-file-btn';
            removeBtn.innerHTML = '×';
            removeBtn.title = 'Remove file';
            removeBtn.onclick = (e) => {
                e.stopPropagation();
                this.removeFile(index);
            };
            
            // Assemble preview item
            previewItem.appendChild(img);
            previewItem.appendChild(fileName);
            previewItem.appendChild(fileSize);
            previewItem.appendChild(removeBtn);
            
            this.filePreviewContainer.appendChild(previewItem);
        });
    }
    
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        
        if (this.selectedFiles.length === 0) {
            this.clearSelection();
        } else {
            this.displayFilePreview();
            this.updateFileCount();
        }
    }
    
    clearSelection() {
        this.selectedFiles = [];
        this.fileInput.value = '';
        this.selectedFilesArea.style.display = 'none';
        this.filePreviewContainer.innerHTML = '';
        this.hideProgress();
        this.dialogState = 'closed';
    }
    
    updateFileCount() {
        if (this.fileCount) {
            this.fileCount.textContent = this.selectedFiles.length;
        }
    }
    
    setupDragAndDrop() {
        if (!this.uploadArea) return;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, (e) => {
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
                e.preventDefault();
                e.stopPropagation();
            });
        });
<<<<<<< HEAD
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            });
        });
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            });
        });
        uploadArea.addEventListener('drop', (e) => {
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                const validFiles = this.validateFiles(files);
                if (validFiles.length > 0) {
                    this.selectedFiles = [...this.selectedFiles, ...validFiles];
                    this.updateFileDisplay();
                    this.showMessage(`Added ${validFiles.length} files via drag and drop`, 'success');
                }
=======
        
        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => {
                this.uploadArea.classList.add('dragover');
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => {
                this.uploadArea.classList.remove('dragover');
            });
        });
        
        this.uploadArea.addEventListener('drop', (e) => {
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                // Set files to input and trigger change
                const dt = new DataTransfer();
                files.forEach(file => dt.items.add(file));
                this.fileInput.files = dt.files;
                
                // Trigger change event
                this.handleFileSelection({ target: { files: dt.files } });
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
            }
        });
    }
    
<<<<<<< HEAD
    async handleFormSubmit(event) {
        event.preventDefault();
=======
    async handleUpload() {
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
        if (this.selectedFiles.length === 0) {
            this.showMessage('Please select files to upload', 'warning');
            return;
        }
<<<<<<< HEAD
        if (this.isUploading) {
            return;
        }
        await this.uploadFiles();
    }
    
    async uploadFiles() {
        this.isUploading = true;
        this.showProgress();
        const uploadBtn = document.getElementById('uploadBtn');
        if (uploadBtn) {
            uploadBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Uploading...';
            uploadBtn.disabled = true;
        }
        try {
            const formData = new FormData();
            
            // ✅ Add CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content 
                           || document.querySelector('input[name="csrf_token"]')?.value;
            if (csrfToken) {
                formData.append('csrf_token', csrfToken);
            }
            
            // Add files
            this.selectedFiles.forEach(file => {
                formData.append('files[]', file);
            });

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (response.ok && data.success) {
                const uploadedCount = data.files ? data.files.length : this.selectedFiles.length;
                const capturedCount = this.capturedPhotos.length;
                let message = `Successfully uploaded ${uploadedCount} file${uploadedCount > 1 ? 's' : ''}!`;
                if (capturedCount > 0) {
                    message += ` (${capturedCount} captured from camera)`;
                }
                this.showMessage(message, 'success');
                this.resetForm();
                // Redirect to dashboard after short delay
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            } else {
                const errorMessage = data.message || 'Upload failed';
                this.showMessage(errorMessage, 'error');
                if (data.errors && data.errors.length > 0) {
                    this.showMessage(data.errors.join('<br>'), 'warning');
                }
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showMessage(`Upload error: ${error.message}`, 'error');
        } finally {
            this.isUploading = false;
            this.hideProgress();
            if (uploadBtn) {
                uploadBtn.innerHTML = '<i class="bi bi-upload"></i> Upload Photos';
                uploadBtn.disabled = false;
            }
        }
    }
    
    resetForm() {
        this.selectedFiles = [];
        this.capturedPhotos = [];
        const fileInput = document.getElementById('file');
        if (fileInput) {
            fileInput.value = '';
        }
        this.updateFileDisplay();
        this.stopCamera();
    }
    
    showProgress() {
        const progressElement = document.getElementById('uploadProgress');
        if (progressElement) {
            progressElement.style.display = 'block';
            progressElement.className = 'alert alert-info mt-3';
            progressElement.innerHTML = '<i class="bi bi-hourglass-split"></i> Uploading photos...';
=======
        
        if (this.isUploading) {
            console.log('Upload already in progress');
            return;
        }
        
        this.isUploading = true;
        this.showProgress();
        this.uploadBtn.classList.add('loading');
        this.uploadBtn.disabled = true;
        
        try {
            // Create FormData
            const formData = new FormData();
            
            // Add CSRF token
            //const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
            //if (csrfToken) {
            //    formData.append('csrf_token', csrfToken);
            //}
            
            // Add files
            this.selectedFiles.forEach(file => {
                formData.append('photos', file);
            });
            
            // Upload with progress
            const response = await this.uploadWithProgress(formData);
            
            if (response.ok) {
                const result = await response.json();
                this.showMessage(`Successfully uploaded ${result.uploaded || this.selectedFiles.length} photos!`, 'success');
                this.clearSelection();
                
                // Refresh page to show new uploads
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                throw new Error(`Upload failed: ${response.status}`);
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showMessage(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.isUploading = false;
            this.hideProgress();
            this.uploadBtn.classList.remove('loading');
            this.uploadBtn.disabled = false;
        }
    }
    
    uploadWithProgress(formData) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            // Progress handler
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    this.updateProgress(percentComplete, `Uploading ${Math.round(percentComplete)}%`);
                }
            });
            
            // Load handler
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve({
                        ok: true,
                        status: xhr.status,
                        json: () => Promise.resolve(JSON.parse(xhr.responseText || '{}'))
                    });
                } else {
                    reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
                }
            });
            
            // Error handler
            xhr.addEventListener('error', () => {
                reject(new Error('Network error'));
            });
            
            // Open and send
            xhr.open('POST', this.uploadForm.action || '/upload');
            xhr.send(formData);
        });
    }
    
    showProgress() {
        if (this.uploadProgress) {
            this.uploadProgress.style.display = 'block';
            this.updateProgress(0, 'Preparing upload...');
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
        }
    }
    
    hideProgress() {
<<<<<<< HEAD
        const progressElement = document.getElementById('uploadProgress');
        if (progressElement) {
            setTimeout(() => {
                progressElement.style.display = 'none';
            }, 3000);
=======
        if (this.uploadProgress) {
            this.uploadProgress.style.display = 'none';
        }
    }
    
    updateProgress(percent, text) {
        if (this.progressBar) {
            this.progressBar.style.width = `${percent}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = text;
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
        }
    }
    
    showMessage(message, type = 'info') {
<<<<<<< HEAD
        const progressElement = document.getElementById('uploadProgress');
        if (!progressElement) return;
=======
        if (!this.uploadMessages) return;
        
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
<<<<<<< HEAD
        const icon = {
            'success': 'bi-check-circle-fill',
            'error': 'bi-exclamation-triangle-fill',
            'warning': 'bi-exclamation-circle-fill',
            'info': 'bi-info-circle-fill'
        }[type] || 'bi-info-circle-fill';
        progressElement.style.display = 'block';
        progressElement.className = `alert ${alertClass} mt-3`;
        progressElement.innerHTML = `<i class="bi ${icon}"></i> ${message}`;
        // Auto-hide success/info messages
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                progressElement.style.display = 'none';
=======
        
        this.uploadMessages.innerHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                const alert = this.uploadMessages.querySelector('.alert');
                if (alert) {
                    alert.classList.remove('show');
                }
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
            }, 5000);
        }
    }
    
<<<<<<< HEAD
    // Cleanup method
    destroy() {
        this.stopCamera();
=======
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
<<<<<<< HEAD
    console.log('PhotoVault: Initializing upload system...');
    // Ensure only one instance
    if (window.photoVaultUploader) {
        window.photoVaultUploader.destroy();
    }
    window.photoVaultUploader = new PhotoVaultUploader();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.photoVaultUploader) {
        window.photoVaultUploader.destroy();
=======
    console.log('PhotoVault: DOM loaded, initializing uploader...');
    
    // Ensure only one instance
    if (window.photoVaultUploader) {
        console.log('PhotoVault: Uploader already exists, skipping initialization');
        return;
    }
    
    window.photoVaultUploader = new PhotoVaultUploader();
});

// Prevent multiple initializations
window.addEventListener('load', () => {
    if (!window.photoVaultUploader) {
        console.log('PhotoVault: Fallback initialization');
        window.photoVaultUploader = new PhotoVaultUploader();
>>>>>>> d7a78a54c0ad65f18ff94f6c70f442201aeb0f38
    }
});