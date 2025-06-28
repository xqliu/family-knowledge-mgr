/**
 * Family Auto-complete Functionality
 * Enhanced auto-complete for family member names
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeFamilyAutocomplete();
});

function initializeFamilyAutocomplete() {
    const familyInputs = document.querySelectorAll('.family-autocomplete');
    familyInputs.forEach(input => {
        setupAutocomplete(input, 'family');
    });
    
    const locationInputs = document.querySelectorAll('.location-autocomplete');
    locationInputs.forEach(input => {
        setupAutocomplete(input, 'location');
    });
    
    const institutionInputs = document.querySelectorAll('.institution-autocomplete');
    institutionInputs.forEach(input => {
        setupAutocomplete(input, 'institution');
    });
}

function setupAutocomplete(input, type) {
    let dropdown = null;
    let currentIndex = -1;
    let searchTimeout = null;
    
    // Create dropdown container
    function createDropdown() {
        if (dropdown) return dropdown;
        
        dropdown = document.createElement('div');
        dropdown.className = `autocomplete-dropdown ${type}-autocomplete-dropdown`;
        dropdown.setAttribute('data-type', input.dataset.institutionType || 'all');
        
        // Position dropdown
        const rect = input.getBoundingClientRect();
        dropdown.style.width = input.offsetWidth + 'px';
        
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(dropdown);
        
        return dropdown;
    }
    
    // Show dropdown
    function showDropdown() {
        if (!dropdown) return;
        dropdown.classList.add('show');
    }
    
    // Hide dropdown
    function hideDropdown() {
        if (!dropdown) return;
        dropdown.classList.remove('show');
        currentIndex = -1;
    }
    
    // Search for items
    function search(query) {
        if (query.length < 2) {
            hideDropdown();
            return;
        }
        
        showLoading();
        
        // Simulate API call - in real implementation, this would call Django backend
        setTimeout(() => {
            const results = getMockResults(query, type);
            displayResults(results);
        }, 300);
    }
    
    // Show loading state
    function showLoading() {
        const dropdown = createDropdown();
        dropdown.innerHTML = '<div class="autocomplete-loading">搜索中...</div>';
        showDropdown();
    }
    
    // Display search results
    function displayResults(results) {
        const dropdown = createDropdown();
        
        if (results.length === 0) {
            dropdown.innerHTML = '<div class="autocomplete-no-results">未找到匹配结果</div>';
        } else {
            dropdown.innerHTML = results.map((item, index) => 
                `<div class="autocomplete-item" data-index="${index}" data-value="${item.value}">
                    <div class="autocomplete-item-icon"></div>
                    <div class="autocomplete-item-content">
                        <div class="autocomplete-item-main">${item.name}</div>
                        ${item.meta ? `<div class="autocomplete-item-meta">${item.meta}</div>` : ''}
                    </div>
                </div>`
            ).join('');
            
            // Add click handlers
            dropdown.querySelectorAll('.autocomplete-item').forEach(item => {
                item.addEventListener('click', function() {
                    selectItem(this.dataset.value, this.querySelector('.autocomplete-item-main').textContent);
                });
                
                item.addEventListener('mouseenter', function() {
                    currentIndex = parseInt(this.dataset.index);
                    updateSelection();
                });
            });
        }
        
        showDropdown();
    }
    
    // Update visual selection
    function updateSelection() {
        if (!dropdown) return;
        
        const items = dropdown.querySelectorAll('.autocomplete-item');
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === currentIndex);
        });
    }
    
    // Select an item
    function selectItem(value, name) {
        input.value = name;
        input.dataset.selectedValue = value;
        hideDropdown();
        
        // Trigger change event
        input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Store for future suggestions
        storeRecentSelection(type, { value, name });
    }
    
    // Handle keyboard navigation
    function handleKeydown(e) {
        if (!dropdown || !dropdown.classList.contains('show')) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                search(input.value);
            }
            return;
        }
        
        const items = dropdown.querySelectorAll('.autocomplete-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = Math.min(currentIndex + 1, items.length - 1);
                updateSelection();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = Math.max(currentIndex - 1, -1);
                updateSelection();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (currentIndex >= 0 && items[currentIndex]) {
                    const item = items[currentIndex];
                    selectItem(item.dataset.value, item.querySelector('.autocomplete-item-main').textContent);
                }
                break;
                
            case 'Escape':
                hideDropdown();
                break;
        }
    }
    
    // Event listeners
    input.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            search(e.target.value);
        }, 300);
    });
    
    input.addEventListener('keydown', handleKeydown);
    
    input.addEventListener('focus', function() {
        if (this.value.length >= 2) {
            search(this.value);
        }
    });
    
    input.addEventListener('blur', function() {
        // Delay hiding to allow for click events
        setTimeout(() => {
            hideDropdown();
        }, 200);
    });
    
    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !dropdown?.contains(e.target)) {
            hideDropdown();
        }
    });
}

// Mock data for demonstration
function getMockResults(query, type) {
    const mockData = {
        family: [
            { value: '1', name: '张三', meta: '父亲 • 65岁' },
            { value: '2', name: '李四', meta: '母亲 • 62岁' },
            { value: '3', name: '张小明', meta: '儿子 • 25岁' },
            { value: '4', name: '张小红', meta: '女儿 • 23岁' }
        ],
        location: [
            { value: '1', name: '北京市朝阳区', meta: '常住地址' },
            { value: '2', name: '上海市浦东新区', meta: '工作地点' },
            { value: '3', name: '广州市天河区', meta: '出生地' },
            { value: '4', name: '深圳市南山区', meta: '旅游地点' }
        ],
        institution: [
            { value: '1', name: '北京协和医院', meta: '三甲医院' },
            { value: '2', name: '清华大学', meta: '985高校' },
            { value: '3', name: '腾讯科技', meta: '互联网公司' },
            { value: '4', name: '中国银行', meta: '国有银行' }
        ]
    };
    
    const data = mockData[type] || [];
    return data.filter(item => 
        item.name.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 8); // Limit to 8 results
}

// Store recent selections for better suggestions
function storeRecentSelection(type, item) {
    const key = `recent_${type}`;
    let recent = JSON.parse(localStorage.getItem(key) || '[]');
    
    // Remove if already exists
    recent = recent.filter(r => r.value !== item.value);
    
    // Add to beginning
    recent.unshift(item);
    
    // Keep only last 10
    recent = recent.slice(0, 10);
    
    localStorage.setItem(key, JSON.stringify(recent));
}

// Get recent selections
function getRecentSelections(type) {
    const key = `recent_${type}`;
    return JSON.parse(localStorage.getItem(key) || '[]');
}

// Enhanced search with recent items
function enhancedSearch(query, type) {
    const results = getMockResults(query, type);
    const recent = getRecentSelections(type);
    
    // Add recent items if query is short
    if (query.length < 3) {
        const recentResults = recent
            .filter(item => item.name.toLowerCase().includes(query.toLowerCase()))
            .map(item => ({ ...item, frequent: true }));
        
        return [...recentResults, ...results.filter(r => 
            !recentResults.some(rr => rr.value === r.value)
        )];
    }
    
    return results;
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeFamilyAutocomplete);
} else {
    initializeFamilyAutocomplete();
}