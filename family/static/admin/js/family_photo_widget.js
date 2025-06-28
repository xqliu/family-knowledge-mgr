/**
 * Family Photo Upload Widget JavaScript
 * Enhanced drag-and-drop photo upload functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initializePhotoWidgets();
});

function initializePhotoWidgets() {
    const photoInputs = document.querySelectorAll('.family-photo-upload');
    photoInputs.forEach(input => {
        setupPhotoWidget(input);
    });
}

function setupPhotoWidget(input) {
    const wrapper = input.closest('.photo-upload-wrapper') || input.parentElement;
    const dropZone = wrapper.querySelector('.photo-drop-zone');
    const preview = wrapper.querySelector('.photo-preview');
    
    if (!dropZone) return;
    
    // Click to upload
    dropZone.addEventListener('click', function() {
        input.click();
    });
    
    // File input change
    input.addEventListener('change', function(e) {
        const files = e.target.files;
        if (files.length > 0) {
            handleFileUpload(files[0], wrapper);
        }
    });
    
    // Drag and drop events
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        // Only remove drag-over if we're actually leaving the drop zone
        if (!this.contains(e.relatedTarget)) {
            this.classList.remove('drag-over');
        }
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            // Update the file input
            const dt = new DataTransfer();
            dt.items.add(files[0]);
            input.files = dt.files;
            
            handleFileUpload(files[0], wrapper);
        }
    });
    
    // Prevent default drag behaviors on document
    document.addEventListener('dragover', function(e) {
        e.preventDefault();
    });
    
    document.addEventListener('drop', function(e) {
        e.preventDefault();
    });
}

function handleFileUpload(file, wrapper) {
    // Validate file
    const validation = validateFile(file);
    if (!validation.valid) {
        showError(wrapper, validation.message);
        return;
    }
    
    // Clear any previous errors
    clearMessages(wrapper);
    
    // Show preview
    showPreview(file, wrapper);
    
    // Show success message
    showSuccess(wrapper, '照片已选择，准备上传');
}

function validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    
    if (!allowedTypes.includes(file.type)) {
        return {
            valid: false,
            message: '只支持 JPG, PNG, GIF, WebP 格式的图片'
        };
    }
    
    if (file.size > maxSize) {
        return {
            valid: false,
            message: '文件大小不能超过 10MB'
        };
    }
    
    return { valid: true };
}

function showPreview(file, wrapper) {
    const preview = wrapper.querySelector('.photo-preview');
    const dropZoneContent = wrapper.querySelector('.drop-zone-content');
    
    if (!preview) return;
    
    // Create preview elements if they don't exist
    let previewImg = preview.querySelector('.preview-image');
    let fileName = preview.querySelector('.file-name');
    let fileSize = preview.querySelector('.file-size');
    
    if (!previewImg) {
        previewImg = document.createElement('img');
        previewImg.className = 'preview-image';
        preview.appendChild(previewImg);
    }
    
    if (!fileName) {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'preview-info';
        
        fileName = document.createElement('span');
        fileName.className = 'file-name';
        
        fileSize = document.createElement('span');
        fileSize.className = 'file-size';
        
        infoDiv.appendChild(fileName);
        infoDiv.appendChild(fileSize);
        preview.appendChild(infoDiv);
    }
    
    // Add remove button if it doesn't exist
    let removeBtn = preview.querySelector('.remove-photo');
    if (!removeBtn) {
        removeBtn = document.createElement('button');
        removeBtn.className = 'remove-photo';
        removeBtn.innerHTML = '×';
        removeBtn.type = 'button';
        removeBtn.title = '移除照片';
        removeBtn.addEventListener('click', function() {
            removePhoto(wrapper);
        });
        preview.appendChild(removeBtn);
    }
    
    // Create file reader
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImg.src = e.target.result;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Hide drop zone content and show preview
        if (dropZoneContent) {
            dropZoneContent.style.display = 'none';
        }
        preview.style.display = 'flex';
    };
    
    reader.readAsDataURL(file);
}

function removePhoto(wrapper) {
    const input = wrapper.querySelector('.family-photo-upload');
    const preview = wrapper.querySelector('.photo-preview');
    const dropZoneContent = wrapper.querySelector('.drop-zone-content');
    
    // Clear the file input
    input.value = '';
    
    // Hide preview and show drop zone content
    if (preview) {
        preview.style.display = 'none';
    }
    
    if (dropZoneContent) {
        dropZoneContent.style.display = 'block';
    }
    
    // Clear messages
    clearMessages(wrapper);
}

function showError(wrapper, message) {
    clearMessages(wrapper);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'photo-upload-error';
    errorDiv.textContent = message;
    
    wrapper.appendChild(errorDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

function showSuccess(wrapper, message) {
    clearMessages(wrapper);
    
    const successDiv = document.createElement('div');
    successDiv.className = 'photo-upload-success';
    successDiv.textContent = message;
    
    wrapper.appendChild(successDiv);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (successDiv.parentElement) {
            successDiv.remove();
        }
    }, 3000);
}

function clearMessages(wrapper) {
    const messages = wrapper.querySelectorAll('.photo-upload-error, .photo-upload-success');
    messages.forEach(msg => msg.remove());
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 字节';
    
    const k = 1024;
    const sizes = ['字节', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Global functions for use in HTML
window.handlePhotoDrop = function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const dropZone = e.currentTarget;
    dropZone.classList.remove('drag-over');
    
    const wrapper = dropZone.closest('.photo-upload-wrapper');
    const input = wrapper.querySelector('.family-photo-upload');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const dt = new DataTransfer();
        dt.items.add(files[0]);
        input.files = dt.files;
        
        handleFileUpload(files[0], wrapper);
    }
};

window.handlePhotoDragOver = function(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
};

window.handlePhotoDragLeave = function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const dropZone = e.currentTarget;
    if (!dropZone.contains(e.relatedTarget)) {
        dropZone.classList.remove('drag-over');
    }
};

window.removePhotoPreview = function(button) {
    const wrapper = button.closest('.photo-upload-wrapper');
    removePhoto(wrapper);
};

// Initialize on dynamic content load
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    const photoInputs = node.querySelectorAll ? node.querySelectorAll('.family-photo-upload') : [];
                    photoInputs.forEach(input => {
                        if (!input.dataset.initialized) {
                            setupPhotoWidget(input);
                            input.dataset.initialized = 'true';
                        }
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}