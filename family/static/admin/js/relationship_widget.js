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
    
    // Update tags display
    updateSelectedTags(selectWidget);
    
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
    
    // Update tags display
    updateSelectedTags(selectWidget);
}

function updateSelectedTags(selectWidget) {
    const container = selectWidget.closest('.relationship-widget-container');
    if (!container) return;
    
    const tagsContainer = container.querySelector('.selected-tags');
    const clearBtn = container.querySelector('.clear-all-btn');
    if (!tagsContainer) return;
    
    // Clear existing tags
    tagsContainer.innerHTML = '';
    
    const selectedRelations = Array.from(selectWidget.selectedOptions);
    
    // Update clear button state
    if (clearBtn) {
        clearBtn.disabled = selectedRelations.length === 0;
    }
    
    // Create tags for each selected relation
    selectedRelations.forEach(option => {
        const relation = option.text;
        const tag = createRelationTag(relation, selectWidget);
        tagsContainer.appendChild(tag);
    });
    
    // Show empty state if no selections
    if (selectedRelations.length === 0) {
        const emptyTag = document.createElement('span');
        emptyTag.className = 'empty-selection';
        emptyTag.textContent = '未选择关系';
        emptyTag.style.color = 'var(--family-text-secondary)';
        emptyTag.style.fontStyle = 'italic';
        emptyTag.style.fontSize = '0.85rem';
        tagsContainer.appendChild(emptyTag);
    }
}

function createRelationTag(relation, selectWidget) {
    const tag = document.createElement('span');
    const relationType = getRelationType(relation);
    tag.className = `selected-tag ${relationType}`;
    
    tag.innerHTML = `
        ${relation}
        <button type="button" class="remove-tag" onclick="removeRelationTag('${relation}', this)" title="移除">×</button>
    `;
    
    return tag;
}

function getRelationType(relation) {
    const bloodRelations = ['父亲', '母亲', '儿子', '女儿', '兄弟', '姐妹'];
    const marriageRelations = ['配偶', '岳父', '岳母', '女婿', '儿媳'];
    
    if (bloodRelations.includes(relation)) return 'blood';
    if (marriageRelations.includes(relation)) return 'marriage';
    return 'other';
}

// Global functions for HTML onclick handlers
window.removeRelationTag = function(relation, tagButton) {
    const container = tagButton.closest('.relationship-widget-container');
    if (!container) return;
    
    const selectWidget = container.querySelector('.relationship-selector');
    const relationBtn = container.querySelector(`[data-relation="${relation}"]`);
    
    if (selectWidget && relationBtn) {
        // Find and deselect the option
        const option = Array.from(selectWidget.options).find(opt => opt.text === relation);
        if (option) {
            option.selected = false;
        }
        
        // Update button state
        relationBtn.classList.remove('selected');
        
        // Update display
        updateSelectedTags(selectWidget);
        
        // Trigger change event
        selectWidget.dispatchEvent(new Event('change', { bubbles: true }));
    }
};

window.clearAllRelations = function(fieldName) {
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
        // Deselect all options
        Array.from(selectWidget.options).forEach(option => {
            option.selected = false;
        });
        
        // Update all button states
        relationBtns.forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Update display
        updateSelectedTags(selectWidget);
        
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