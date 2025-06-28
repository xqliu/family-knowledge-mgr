/**
 * Family Date Widget JavaScript
 * Enhanced date picker with quick selection buttons
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeDateWidgets();
});

function initializeDateWidgets() {
    const dateInputs = document.querySelectorAll('.family-date-picker');
    dateInputs.forEach(input => {
        setupDateWidget(input);
    });
    
    // Setup quick date buttons
    const quickDateBtns = document.querySelectorAll('.quick-date-btn');
    quickDateBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            handleQuickDate(this);
        });
    });
}

function setupDateWidget(input) {
    // Add change event listener for age calculation
    input.addEventListener('change', function() {
        calculateAge(this);
        validateDate(this);
    });
    
    // Add focus event for mobile optimization
    input.addEventListener('focus', function() {
        if ('ontouchstart' in window) {
            // Scroll to input on mobile to ensure visibility
            setTimeout(() => {
                this.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        }
    });
}

function handleQuickDate(button) {
    const wrapper = button.closest('.quick-dates-wrapper') || button.parentElement.parentElement;
    const dateInput = wrapper.previousElementSibling || wrapper.parentElement.querySelector('.family-date-picker');
    
    if (!dateInput) {
        console.warn('Could not find associated date input');
        return;
    }
    
    if (button.dataset.clear === 'true') {
        // Clear the date
        dateInput.value = '';
        clearMessages(dateInput);
        button.classList.add('selected');
        setTimeout(() => button.classList.remove('selected'), 300);
        return;
    }
    
    const days = parseInt(button.dataset.days) || 0;
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + days);
    
    // Format date as YYYY-MM-DD for input[type="date"]
    const formattedDate = targetDate.toISOString().split('T')[0];
    dateInput.value = formattedDate;
    
    // Trigger change event
    dateInput.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Visual feedback
    button.classList.add('selected');
    setTimeout(() => button.classList.remove('selected'), 300);
    
    // Calculate age if this is a birth date field
    calculateAge(dateInput);
}

function calculateAge(dateInput) {
    const fieldName = dateInput.name.toLowerCase();
    if (!fieldName.includes('birth') && !fieldName.includes('生日')) {
        return;
    }
    
    const birthDate = new Date(dateInput.value);
    if (isNaN(birthDate.getTime())) {
        hideAgeDisplay(dateInput);
        return;
    }
    
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    showAgeDisplay(dateInput, age);
}

function showAgeDisplay(dateInput, age) {
    const wrapper = dateInput.parentElement;
    let ageDisplay = wrapper.querySelector('.age-display');
    
    if (!ageDisplay) {
        ageDisplay = document.createElement('div');
        ageDisplay.className = 'age-display';
        wrapper.appendChild(ageDisplay);
    }
    
    if (age >= 0) {
        ageDisplay.textContent = `年龄: ${age}岁`;
        ageDisplay.classList.add('highlight');
    } else {
        ageDisplay.textContent = '出生日期不能是未来的日期';
        ageDisplay.classList.remove('highlight');
    }
    
    ageDisplay.style.display = 'block';
}

function hideAgeDisplay(dateInput) {
    const wrapper = dateInput.parentElement;
    const ageDisplay = wrapper.querySelector('.age-display');
    if (ageDisplay) {
        ageDisplay.style.display = 'none';
    }
}

function validateDate(dateInput) {
    const date = new Date(dateInput.value);
    const today = new Date();
    const fieldName = dateInput.name.toLowerCase();
    
    clearMessages(dateInput);
    
    if (isNaN(date.getTime())) {
        return;
    }
    
    // Validate birth dates
    if (fieldName.includes('birth') || fieldName.includes('生日')) {
        if (date > today) {
            showValidationMessage(dateInput, '出生日期不能是未来的日期', 'error');
            return;
        }
        
        // Check for very old dates (more than 150 years ago)
        const maxAge = new Date();
        maxAge.setFullYear(maxAge.getFullYear() - 150);
        if (date < maxAge) {
            showValidationMessage(dateInput, '请检查出生日期是否正确', 'warning');
            return;
        }
    }
    
    // Validate death dates
    if (fieldName.includes('death') || fieldName.includes('逝世')) {
        if (date > today) {
            showValidationMessage(dateInput, '逝世日期不能是未来的日期', 'error');
            return;
        }
    }
    
    // Success message for valid dates
    if (fieldName.includes('birth') || fieldName.includes('生日')) {
        showValidationMessage(dateInput, '日期格式正确', 'success');
        setTimeout(() => clearMessages(dateInput), 2000);
    }
}

function showValidationMessage(dateInput, message, type) {
    const wrapper = dateInput.parentElement;
    let messageDiv = wrapper.querySelector('.date-validation-message');
    
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.className = 'date-validation-message';
        wrapper.appendChild(messageDiv);
    }
    
    messageDiv.textContent = message;
    messageDiv.className = `date-validation-message ${type} show`;
}

function clearMessages(dateInput) {
    const wrapper = dateInput.parentElement;
    const messages = wrapper.querySelectorAll('.date-validation-message');
    messages.forEach(msg => {
        msg.classList.remove('show');
        setTimeout(() => {
            if (msg.parentElement) {
                msg.remove();
            }
        }, 300);
    });
}

// Global functions for use in HTML onclick handlers
window.setFamilyDate = function(button, fieldName, days) {
    const container = button.closest('.family-date-container');
    const input = container.querySelector('.family-date-picker') || 
                  container.querySelector(`input[name="${fieldName}"]`) ||
                  document.querySelector(`input[name="${fieldName}"]`);
    
    if (!input) {
        console.warn('Could not find date input for field:', fieldName);
        return;
    }
    
    const today = new Date();
    const targetDate = new Date(today.getTime() + (days * 24 * 60 * 60 * 1000));
    
    // Format date as YYYY-MM-DD for input[type="date"]
    const formattedDate = targetDate.toISOString().split('T')[0];
    input.value = formattedDate;
    
    // Trigger change event
    input.dispatchEvent(new Event('change', { bubbles: true }));
    input.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Visual feedback
    button.classList.add('selected');
    setTimeout(() => button.classList.remove('selected'), 300);
    
    // Calculate age if this is a birth date field
    calculateAge(input);
    
    console.log(`Set ${fieldName} to ${formattedDate}`);
};

window.clearFamilyDate = function(button, fieldName) {
    const container = button.closest('.family-date-container');
    const input = container.querySelector('.family-date-picker') || 
                  container.querySelector(`input[name="${fieldName}"]`) ||
                  document.querySelector(`input[name="${fieldName}"]`);
    
    if (!input) {
        console.warn('Could not find date input for field:', fieldName);
        return;
    }
    
    input.value = '';
    
    // Trigger change event
    input.dispatchEvent(new Event('change', { bubbles: true }));
    input.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Visual feedback
    button.classList.add('selected');
    setTimeout(() => button.classList.remove('selected'), 300);
    
    // Hide age display
    hideAgeDisplay(input);
    clearMessages(input);
    
    console.log(`Cleared ${fieldName}`);
};

// Legacy function for backwards compatibility
window.setQuickDate = function(button, type) {
    const wrapper = button.parentElement.parentElement;
    const input = wrapper.querySelector('.family-date-picker') || 
                  wrapper.previousElementSibling ||
                  document.querySelector('.family-date-picker');
    
    if (!input) return;
    
    const today = new Date();
    let targetDate;
    
    switch(type) {
        case 'today':
            targetDate = today;
            break;
        case 'yesterday':
            targetDate = new Date(today.getTime() - 24 * 60 * 60 * 1000);
            break;
        case 'week':
            targetDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case 'month':
            targetDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            break;
        default:
            return;
    }
    
    input.value = targetDate.toISOString().split('T')[0];
    input.dispatchEvent(new Event('change'));
    
    // Visual feedback
    button.classList.add('selected');
    setTimeout(() => button.classList.remove('selected'), 300);
};

// Initialize on dynamic content load
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    const dateInputs = node.querySelectorAll ? node.querySelectorAll('.family-date-picker') : [];
                    dateInputs.forEach(input => {
                        if (!input.dataset.initialized) {
                            setupDateWidget(input);
                            input.dataset.initialized = 'true';
                        }
                    });
                    
                    const quickBtns = node.querySelectorAll ? node.querySelectorAll('.quick-date-btn') : [];
                    quickBtns.forEach(btn => {
                        if (!btn.dataset.initialized) {
                            btn.addEventListener('click', function() {
                                handleQuickDate(this);
                            });
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
    document.addEventListener('DOMContentLoaded', initializeDateWidgets);
} else {
    initializeDateWidgets();
}

// Also initialize after a short delay to catch any dynamically loaded content
setTimeout(initializeDateWidgets, 500);

// Ensure global functions are available immediately
console.log('Family date widget JavaScript loaded, functions available:', {
    setFamilyDate: typeof window.setFamilyDate,
    clearFamilyDate: typeof window.clearFamilyDate
});