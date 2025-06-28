/**
 * Relationship Widget JavaScript
 * Handles interactive relationship selection and family tree visualization
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeRelationshipWidgets();
});

function initializeRelationshipWidgets() {
    const relationshipVisuals = document.querySelectorAll('.relationship-visual');
    relationshipVisuals.forEach(visual => {
        setupRelationshipWidget(visual);
    });
}

function setupRelationshipWidget(visual) {
    const relationBtns = visual.querySelectorAll('.relation-btn');
    const selectWidget = visual.parentElement.querySelector('.relationship-selector');
    
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
    
    // Update family tree visualization
    updateFamilyTreeVisualization(selectWidget);
}

function updateButtonStates(selectWidget, relationBtns) {
    const selectedRelations = Array.from(selectWidget.selectedOptions).map(opt => opt.text);
    
    relationBtns.forEach(btn => {
        const relation = btn.dataset.relation;
        const isSelected = selectedRelations.includes(relation);
        btn.classList.toggle('selected', isSelected);
    });
}

function updateFamilyTreeVisualization(selectWidget) {
    const visual = selectWidget.parentElement.querySelector('.relationship-visual');
    if (!visual) return;
    
    const treeNodes = visual.querySelectorAll('.tree-node');
    const selectedRelations = Array.from(selectWidget.selectedOptions).map(opt => opt.text);
    
    // Reset all nodes
    treeNodes.forEach(node => {
        node.classList.remove('has-relation');
        node.style.opacity = '0.7';
    });
    
    // Highlight relevant generations based on selected relations
    selectedRelations.forEach(relation => {
        highlightRelevantGeneration(relation, treeNodes);
    });
    
    // If no relations selected, show all generations normally
    if (selectedRelations.length === 0) {
        treeNodes.forEach(node => {
            node.style.opacity = '1';
        });
    }
}

function highlightRelevantGeneration(relation, treeNodes) {
    const relationToGeneration = {
        // Parents generation
        '父亲': 'parents',
        '母亲': 'parents',
        '岳父': 'parents',
        '岳母': 'parents',
        
        // Grandparents generation
        '祖父': 'grandparents',
        '祖母': 'grandparents',
        '外祖父': 'grandparents',
        '外祖母': 'grandparents',
        
        // Current generation
        '配偶': 'self',
        '兄弟': 'self',
        '姐妹': 'self',
        '朋友': 'self',
        '同事': 'self',
        '邻居': 'self',
        
        // Children generation
        '儿子': 'children',
        '女儿': 'children',
        '女婿': 'children',
        '儿媳': 'children',
        
        // Grandchildren generation
        '孙子': 'grandchildren',
        '孙女': 'grandchildren',
        '外孙': 'grandchildren',
        '外孙女': 'grandchildren'
    };
    
    const generation = relationToGeneration[relation];
    if (generation) {
        const node = Array.from(treeNodes).find(node => node.classList.contains(generation));
        if (node) {
            node.classList.add('has-relation');
            node.style.opacity = '1';
            node.style.transform = 'scale(1.05)';
            setTimeout(() => {
                node.style.transform = '';
            }, 200);
        }
    }
}

// Global function for use in HTML onclick handlers
window.selectRelation = function(relation, selectId) {
    const selectWidget = document.getElementById(selectId);
    if (!selectWidget) return;
    
    const visual = selectWidget.parentElement.querySelector('.relationship-visual');
    if (!visual) return;
    
    const button = visual.querySelector(`[data-relation="${relation}"]`);
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
                    const relationshipVisuals = node.querySelectorAll ? node.querySelectorAll('.relationship-visual') : [];
                    relationshipVisuals.forEach(visual => {
                        if (!visual.dataset.initialized) {
                            setupRelationshipWidget(visual);
                            visual.dataset.initialized = 'true';
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