/**
 * Inline Create Widget JavaScript
 * Handles popup creation of related objects in admin forms
 */

// Global variables
let currentModal = null;
let currentFieldName = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeInlineCreate();
});

function initializeInlineCreate() {
    // Setup existing inline create buttons
    const inlineCreateBtns = document.querySelectorAll('.inline-create-btn');
    inlineCreateBtns.forEach(btn => {
        if (!btn.dataset.initialized) {
            btn.addEventListener('click', handleInlineCreateClick);
            btn.dataset.initialized = 'true';
        }
    });
}

function handleInlineCreateClick(event) {
    event.preventDefault();
    const button = event.currentTarget;
    const url = button.href;
    const fieldName = button.dataset.fieldName || button.closest('.inline-create-wrapper').querySelector('select, input').name;
    
    showInlineCreatePopup(button, fieldName);
}

function showInlineCreatePopup(button, fieldName) {
    const url = button.href;
    currentFieldName = fieldName;
    
    // Create modal if it doesn't exist
    if (!currentModal) {
        createModal();
    }
    
    // Show loading state
    showModalLoading();
    
    // Fetch the form
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'text/html,application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.text();
    })
    .then(html => {
        showModalForm(html, url);
    })
    .catch(error => {
        console.error('Error loading inline create form:', error);
        showModalError('加载表单时出错: ' + error.message);
    });
    
    return false;
}

function createModal() {
    const modal = document.createElement('div');
    modal.className = 'inline-create-modal';
    modal.innerHTML = `
        <div class="inline-create-modal-content">
            <div class="modal-header">
                <h3 class="modal-title">新建</h3>
                <button type="button" class="modal-close" onclick="closeInlineCreateModal()">&times;</button>
            </div>
            <div class="modal-body">
                <!-- Content will be loaded here -->
            </div>
            <div class="modal-footer">
                <button type="button" class="modal-btn modal-btn-secondary" onclick="closeInlineCreateModal()">取消</button>
                <button type="button" class="modal-btn modal-btn-primary" onclick="submitInlineCreateForm()">保存</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    currentModal = modal;
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeInlineCreateModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && currentModal && currentModal.classList.contains('show')) {
            closeInlineCreateModal();
        }
    });
}

function showModalLoading() {
    const modalBody = currentModal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="inline-create-loading">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
        </div>
    `;
    
    currentModal.classList.add('show');
}

function showModalForm(html, formUrl) {
    const modalBody = currentModal.querySelector('.modal-body');
    const modalTitle = currentModal.querySelector('.modal-title');
    
    // Extract form from the response
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    const form = tempDiv.querySelector('form') || tempDiv;
    const title = tempDiv.querySelector('h1, h2, h3')?.textContent || '新建记录';
    
    modalTitle.textContent = title;
    modalBody.innerHTML = `<form class="modal-form" action="${formUrl}" method="post"></form>`;
    
    const modalForm = modalBody.querySelector('.modal-form');
    
    // Copy form content
    while (form.firstChild) {
        modalForm.appendChild(form.firstChild);
    }
    
    // Remove submit buttons from the form (we'll use our own)
    const submitBtns = modalForm.querySelectorAll('input[type="submit"], button[type="submit"]');
    submitBtns.forEach(btn => btn.remove());
    
    // Add CSRF token if not present
    if (!modalForm.querySelector('input[name="csrfmiddlewaretoken"]')) {
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfToken) {
            modalForm.appendChild(csrfToken.cloneNode(true));
        }
    }
    
    // Initialize any widgets in the form
    initializeFormWidgets(modalForm);
    
    currentModal.classList.add('show');
}

function showModalError(message) {
    const modalBody = currentModal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="inline-create-error">
            <strong>错误:</strong> ${message}
        </div>
    `;
    
    currentModal.classList.add('show');
}

function submitInlineCreateForm() {
    const form = currentModal.querySelector('.modal-form');
    if (!form) {
        console.error('No form found in modal');
        return;
    }
    
    // Show loading state on submit button
    const submitBtn = currentModal.querySelector('.modal-btn-primary');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '保存中...';
    submitBtn.disabled = true;
    
    // Clear any previous errors
    const existingErrors = currentModal.querySelectorAll('.inline-create-error');
    existingErrors.forEach(error => error.remove());
    
    // Prepare form data
    const formData = new FormData(form);
    
    // Submit form
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Success - add the new option to the original field
            addNewOptionToField(data);
            showSuccessMessage(`成功创建: ${data.name}`);
            setTimeout(() => {
                closeInlineCreateModal();
            }, 1000);
        } else {
            // Show errors
            showFormErrors(data.errors);
        }
    })
    .catch(error => {
        console.error('Error submitting form:', error);
        showModalError('提交表单时出错: ' + error.message);
    })
    .finally(() => {
        // Restore submit button
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

function addNewOptionToField(data) {
    // Find the target field
    const field = document.querySelector(`[name="${currentFieldName}"]`);
    if (!field) {
        console.warn('Could not find target field:', currentFieldName);
        return;
    }
    
    if (field.tagName === 'SELECT') {
        // Add new option to select field
        const option = document.createElement('option');
        option.value = data.id;
        option.textContent = data.name;
        option.selected = true;
        field.appendChild(option);
        
        // If it's a multiple select, trigger change event
        if (field.multiple) {
            field.dispatchEvent(new Event('change', { bubbles: true }));
        }
    } else if (field.classList.contains('vManyToManyRawIdAdminField')) {
        // Handle raw ID widget
        const currentValue = field.value;
        const newValue = currentValue ? `${currentValue},${data.id}` : data.id;
        field.value = newValue;
        field.dispatchEvent(new Event('change', { bubbles: true }));
    }
    
    // Update any associated display elements
    updateRelatedDisplays(field, data);
}

function updateRelatedDisplays(field, data) {
    // Update any related display spans or divs
    const fieldWrapper = field.closest('.form-row, .field-box, .inline-create-wrapper');
    if (fieldWrapper) {
        const displays = fieldWrapper.querySelectorAll('.related-widget-wrapper-link, .related-lookup');
        displays.forEach(display => {
            // Update display text if needed
            if (display.textContent.trim() === '' || display.textContent.includes('无')) {
                display.textContent = data.name;
            }
        });
    }
}

function showFormErrors(errors) {
    const modalBody = currentModal.querySelector('.modal-body');
    
    // Create error container
    const errorDiv = document.createElement('div');
    errorDiv.className = 'inline-create-error';
    
    let errorHtml = '<strong>请修正以下错误:</strong><ul class="error-list">';
    
    for (const [field, fieldErrors] of Object.entries(errors)) {
        if (Array.isArray(fieldErrors)) {
            fieldErrors.forEach(error => {
                errorHtml += `<li>${field}: ${error}</li>`;
            });
        } else {
            errorHtml += `<li>${field}: ${fieldErrors}</li>`;
        }
    }
    
    errorHtml += '</ul>';
    errorDiv.innerHTML = errorHtml;
    
    // Insert at the beginning of modal body
    modalBody.insertBefore(errorDiv, modalBody.firstChild);
}

function showSuccessMessage(message) {
    const modalBody = currentModal.querySelector('.modal-body');
    
    const successDiv = document.createElement('div');
    successDiv.className = 'inline-create-success';
    successDiv.innerHTML = `
        <span class="success-icon"></span>
        <span>${message}</span>
    `;
    
    // Insert at the beginning of modal body
    modalBody.insertBefore(successDiv, modalBody.firstChild);
}

function closeInlineCreateModal() {
    if (currentModal) {
        currentModal.classList.remove('show');
        currentFieldName = null;
        
        // Remove modal after animation
        setTimeout(() => {
            if (currentModal && currentModal.parentNode) {
                currentModal.parentNode.removeChild(currentModal);
                currentModal = null;
            }
        }, 300);
    }
}

function initializeFormWidgets(form) {
    // Initialize any special widgets in the form
    
    // Date widgets
    const dateInputs = form.querySelectorAll('.family-date-picker');
    dateInputs.forEach(input => {
        if (typeof setupDateWidget === 'function') {
            setupDateWidget(input);
        }
    });
    
    // Auto-complete widgets
    const autoCompleteInputs = form.querySelectorAll('.family-autocomplete, .location-autocomplete, .institution-autocomplete');
    autoCompleteInputs.forEach(input => {
        if (typeof initializeAutoComplete === 'function') {
            initializeAutoComplete(input);
        }
    });
    
    // Rich text widgets
    const richTextAreas = form.querySelectorAll('.rich-text-editor');
    richTextAreas.forEach(textarea => {
        if (typeof initializeRichText === 'function') {
            initializeRichText(textarea);
        }
    });
}

// Global function for use in HTML onclick handlers
window.showInlineCreatePopup = showInlineCreatePopup;
window.closeInlineCreateModal = closeInlineCreateModal;
window.submitInlineCreateForm = submitInlineCreateForm;

// Initialize on dynamic content load
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    const inlineCreateBtns = node.querySelectorAll ? node.querySelectorAll('.inline-create-btn') : [];
                    inlineCreateBtns.forEach(btn => {
                        if (!btn.dataset.initialized) {
                            btn.addEventListener('click', handleInlineCreateClick);
                            btn.dataset.initialized = 'true';
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

// Initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeInlineCreate);
} else {
    initializeInlineCreate();
}

console.log('Inline create widget JavaScript loaded');