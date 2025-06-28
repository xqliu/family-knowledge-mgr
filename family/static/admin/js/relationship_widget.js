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
    
    // Initialize button states and tags based on current selection
    updateButtonStates(selectWidget, relationBtns);
    
    // Listen for changes in the select widget
    selectWidget.addEventListener('change', function() {
        updateButtonStates(this, relationBtns);
    });
}

function handleRelationSelection(button, selectWidget) {
    const relation = button.dataset.relation;
    if (!relation) return;
    
    const container = selectWidget.closest('.relationship-widget-container');
    const allButtons = container.querySelectorAll('.relation-btn');
    
    // Check if this button is already selected
    const isCurrentlySelected = button.classList.contains('selected');
    
    if (isCurrentlySelected) {
        // Deselect if clicking the same button
        button.classList.remove('selected');
        clearSelectWidget(selectWidget);
        updateCurrentSelection(container, null);
    } else {
        // Single-select: deselect all other buttons
        allButtons.forEach(btn => btn.classList.remove('selected'));
        
        // Select this button
        button.classList.add('selected');
        
        // Update select widget
        updateSelectWidget(selectWidget, relation);
        
        // Update display
        const relationType = getRelationType(relation);
        updateCurrentSelection(container, relation, relationType);
        
        // Visual feedback
        button.style.animation = 'relation-selected 0.3s ease-out';
        setTimeout(() => {
            button.style.animation = '';
        }, 300);
    }
    
    // Trigger change event
    selectWidget.dispatchEvent(new Event('change', { bubbles: true }));
}

function updateButtonStates(selectWidget, relationBtns) {
    const container = selectWidget.closest('.relationship-widget-container');
    const selectedRelations = Array.from(selectWidget.selectedOptions).map(opt => opt.text);
    const selectedRelation = selectedRelations.length > 0 ? selectedRelations[0] : null;
    
    // Update button states
    relationBtns.forEach(btn => {
        const relation = btn.dataset.relation;
        const isSelected = selectedRelations.includes(relation);
        btn.classList.toggle('selected', isSelected);
    });
    
    // Update current selection display
    if (selectedRelation) {
        const relationType = getRelationType(selectedRelation);
        updateCurrentSelection(container, selectedRelation, relationType);
    } else {
        updateCurrentSelection(container, null);
    }
}

function updateSelectWidget(selectWidget, relation) {
    // Clear all selections first
    Array.from(selectWidget.options).forEach(option => {
        option.selected = false;
    });
    
    // Find or create the option
    let option = Array.from(selectWidget.options).find(opt => opt.text === relation);
    if (!option) {
        option = document.createElement('option');
        option.value = relation;
        option.text = relation;
        selectWidget.appendChild(option);
    }
    
    // Select the option
    option.selected = true;
}

function clearSelectWidget(selectWidget) {
    Array.from(selectWidget.options).forEach(option => {
        option.selected = false;
    });
}

function updateCurrentSelection(container, relation, relationType = null) {
    const currentSelectionEl = container.querySelector('.current-selection');
    const clearBtn = container.querySelector('.clear-selection-btn');
    
    if (!currentSelectionEl) return;
    
    if (relation) {
        currentSelectionEl.textContent = relation;
        currentSelectionEl.className = `current-selection has-selection ${relationType}`;
        if (clearBtn) clearBtn.disabled = false;
    } else {
        currentSelectionEl.textContent = '未选择';
        currentSelectionEl.className = 'current-selection empty';
        if (clearBtn) clearBtn.disabled = true;
    }
}

function getRelationType(relation) {
    const bloodRelations = ['父亲', '母亲', '儿子', '女儿', '兄弟', '姐妹'];
    const marriageRelations = ['配偶', '岳父', '岳母', '女婿', '儿媳'];
    
    if (bloodRelations.includes(relation)) return 'blood';
    if (marriageRelations.includes(relation)) return 'marriage';
    return 'other';
}

// Global functions for HTML onclick handlers
window.clearSelection = function(fieldName) {
    const containers = document.querySelectorAll('.relationship-widget-container');
    let targetContainer = null;
    
    // Find the correct container by checking the select widget name
    containers.forEach(container => {
        const selectWidget = container.querySelector('.relationship-selector');
        if (selectWidget && selectWidget.name === fieldName) {
            targetContainer = container;
        }
    });
    
    if (!targetContainer) return;
    
    const selectWidget = targetContainer.querySelector('.relationship-selector');
    const relationBtns = targetContainer.querySelectorAll('.relation-btn');
    
    if (selectWidget) {
        // Clear selection
        clearSelectWidget(selectWidget);
        
        // Update all button states
        relationBtns.forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Update display
        updateCurrentSelection(targetContainer, null);
        
        // Trigger change event
        selectWidget.dispatchEvent(new Event('change', { bubbles: true }));
    }
};

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