/**
 * Relationship Widget JavaScript
 * Handles interactive relationship selection and family tree visualization
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeRelationshipWidgets();
});

function initializeRelationshipWidgets() {
    const relationshipContainers = document.querySelectorAll('.relationship-widget-container');
    relationshipContainers.forEach(container => {
        setupRelationshipWidget(container);
    });
}

function setupRelationshipWidget(container) {
    const relationBtns = container.querySelectorAll('.relation-btn');
    const selectWidget = container.querySelector('.relationship-selector');
    
    if (!selectWidget) {
        console.warn('Could not find relationship selector widget');
        return;
    }
    
    // Set up click handlers for relation buttons
    relationBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            handleRelationSelection(this, selectWidget);
        });
    });
    
    // Initialize button states based on current selection
    updateButtonStates(selectWidget, relationBtns);
    
    // Listen for changes in the select widget
    selectWidget.addEventListener('change', function() {
        updateButtonStates(this, relationBtns);
    });
}

function handleRelationSelection(button, selectWidget) {
    const relation = button.dataset.relation;
    if (!relation) return;
    
    // Find or create option in select widget
    let option = Array.from(selectWidget.options).find(opt => opt.text === relation);
    
    if (!option) {
        // Create new option if it doesn't exist
        option = document.createElement('option');
        option.value = relation;
        option.text = relation;
        selectWidget.appendChild(option);
    }
    
    // Toggle selection
    const wasSelected = option.selected;
    option.selected = !wasSelected;
    
    // Update button state
    button.classList.toggle('selected', !wasSelected);
    
    // Trigger change event
    selectWidget.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Visual feedback
    if (!wasSelected) {
        button.classList.add('selected');
        // Brief animation
        setTimeout(() => {
            button.style.animation = 'relation-selected 0.3s ease-out';
            setTimeout(() => {
                button.style.animation = '';
            }, 300);
        }, 10);
    }
    
}

function updateButtonStates(selectWidget, relationBtns) {
    const selectedRelations = Array.from(selectWidget.selectedOptions).map(opt => opt.text);
    
    relationBtns.forEach(btn => {
        const relation = btn.dataset.relation;
        const isSelected = selectedRelations.includes(relation);
        btn.classList.toggle('selected', isSelected);
    });
}

// Global function for use in HTML onclick handlers
window.selectRelation = function(relation, selectId) {
    const selectWidget = document.getElementById(selectId);
    if (!selectWidget) return;
    
    const container = selectWidget.closest('.relationship-widget-container');
    if (!container) return;
    
    const button = container.querySelector(`[data-relation="${relation}"]`);
    if (button) {
        handleRelationSelection(button, selectWidget);
    }
};

// Initialize on dynamic content load
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    const relationshipContainers = node.querySelectorAll ? node.querySelectorAll('.relationship-widget-container') : [];
                    relationshipContainers.forEach(container => {
                        if (!container.dataset.initialized) {
                            setupRelationshipWidget(container);
                            container.dataset.initialized = 'true';
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
    document.addEventListener('DOMContentLoaded', initializeRelationshipWidgets);
} else {
    initializeRelationshipWidgets();
}

// Also initialize after a short delay to catch any dynamically loaded content
setTimeout(initializeRelationshipWidgets, 500);

console.log('Relationship widget JavaScript loaded');