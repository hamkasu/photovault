// Photo Editor functionality
let currentTool = 'move';
let isDrawing = false;
let lastX = 0;
let lastY = 0;
let canvas, ctx, image;
let brightness = 0, contrast = 0, saturation = 0, rotation = 0;

function initEditor() {
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    
    const img = document.getElementById('sourceImage');
    image = new Image();
    image.onload = function() {
        resizeCanvas();
        applyFilters();
    };
    image.src = img.src;
    
    // Add event listeners
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // Add touch support for mobile
    canvas.addEventListener('touchstart', handleTouchStart);
    canvas.addEventListener('touchmove', handleTouchMove);
    canvas.addEventListener('touchend', handleTouchEnd);
    
    // Setup filter controls
    document.getElementById('brightness').addEventListener('input', updateFilter);
    document.getElementById('contrast').addEventListener('input', updateFilter);
    document.getElementById('saturation').addEventListener('input', updateFilter);
    document.getElementById('rotation').addEventListener('input', updateFilter);
    
    // Setup color and line width
    document.getElementById('drawColor').addEventListener('input', updateDrawingStyle);
    document.getElementById('lineWidth').addEventListener('input', updateDrawingStyle);
}

function handleTouchStart(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousedown', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}

function handleTouchMove(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}

function handleTouchEnd(e) {
    e.preventDefault();
    const mouseEvent = new MouseEvent('mouseup', {});
    canvas.dispatchEvent(mouseEvent);
}

function setTool(tool) {
    currentTool = tool;
    // Update UI to show active tool
    document.querySelectorAll('.btn-outline-primary').forEach(btn => {
        btn.classList.remove('tool-active');
    });
    event.target.classList.add('tool-active');
}

function startDrawing(e) {
    if (currentTool === 'move') return;
    
    isDrawing = true;
    [lastX, lastY] = getMousePos(canvas, e);
}

function draw(e) {
    if (!isDrawing) return;
    
    const [x, y] = getMousePos(canvas, e);
    
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.strokeStyle = document.getElementById('drawColor').value;
    ctx.lineWidth = document.getElementById('lineWidth').value;
    ctx.lineCap = 'round';
    ctx.stroke();
    
    [lastX, lastY] = [x, y];
}

function stopDrawing() {
    isDrawing = false;
}

function getMousePos(canvas, evt) {
    const rect = canvas.getBoundingClientRect();
    return [
        (evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width,
        (evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height
    ];
}

function updateFilter() {
    brightness = parseInt(document.getElementById('brightness').value);
    contrast = parseInt(document.getElementById('contrast').value);
    saturation = parseInt(document.getElementById('saturation').value);
    rotation = parseInt(document.getElementById('rotation').value);
    applyFilters();
}

function updateDrawingStyle() {
    // This is handled in the draw function
}

function applyFilters() {
    if (!image) return;
    
    resizeCanvas();
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Save context
    ctx.save();
    
    // Apply rotation
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate(rotation * Math.PI / 180);
    ctx.translate(-canvas.width / 2, -canvas.height / 2);
    
    // Draw image
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    
    // Apply filters if needed (for more advanced filters, you'd use getImageData)
    if (brightness !== 0 || contrast !== 0 || saturation !== 0) {
        // Simple brightness adjustment
        if (brightness !== 0) {
            ctx.fillStyle = `rgba(255, 255, 255, ${brightness / 100})`;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
    }
    
    // Restore context
    ctx.restore();
}

function resizeCanvas() {
    if (!image) return;
    canvas.width = image.width;
    canvas.height = image.height;
}

function saveEdit() {
    if (!canvas) {
        alert('Editor not initialized');
        return;
    }
    
    const dataURL = canvas.toDataURL('image/jpeg', 0.9);
    
    fetch('/api/save-edit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            photo_id: photoId,
            image_data: dataURL
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Changes saved successfully!');
        } else {
            alert('Failed to save changes: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Save error:', error);
        alert('Save error: ' + error.message);
    });
}

function resetImage() {
    // Reset all controls
    document.getElementById('brightness').value = 0;
    document.getElementById('contrast').value = 0;
    document.getElementById('saturation').value = 0;
    document.getElementById('rotation').value = 0;
    
    brightness = 0;
    contrast = 0;
    saturation = 0;
    rotation = 0;
    
    // Reload image
    const img = document.getElementById('sourceImage');
    image.src = img.src;
}

// Initialize editor when page loads
document.addEventListener('DOMContentLoaded', initEditor);
