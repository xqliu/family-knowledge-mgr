/**
 * Family Knowledge Management System - Admin Interface JavaScript
 * Enhanced interactions and mobile optimizations
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeFamilyAdmin();
});

function initializeFamilyAdmin() {
    // Initialize all family admin features
    setupTouchOptimizations();
    setupDashboardAnimations();
    setupMobileNavigation();
    setupPhotoPreview();
    setupFormEnhancements();
    loadFamilyStatistics();
    
    console.log('Family Admin interface initialized');
}

/**
 * Touch-friendly optimizations for mobile devices
 */
function setupTouchOptimizations() {
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Add touch feedback to cards
        const cards = document.querySelectorAll('.quick-action-card, .stat-card');
        cards.forEach(card => {
            card.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            card.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            });
        });
        
        // Improve scroll performance
        document.body.style.webkitOverflowScrolling = 'touch';
    }
}

/**
 * Dashboard animations and loading effects
 */
function setupDashboardAnimations() {
    // Animate dashboard cards on load
    const cards = document.querySelectorAll('.quick-action-card, .stat-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('animate-in');
        }, index * 100);
    });
    
    // Parallax effect for welcome section (desktop only)
    if (window.innerWidth > 768) {
        const welcome = document.querySelector('.dashboard-welcome');
        if (welcome) {
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                welcome.style.transform = `translateY(${rate}px)`;
            });
        }
    }
}

/**
 * Mobile navigation enhancements
 */
function setupMobileNavigation() {
    const navLinks = document.querySelectorAll('.family-nav-link');
    
    // Add active state management
    navLinks.forEach(link => {
        if (window.location.pathname.includes(link.getAttribute('href'))) {
            link.classList.add('active');
        }
        
        // Smooth transitions
        link.addEventListener('click', function(e) {
            // Add loading state
            this.classList.add('loading');
            
            // Remove loading state after navigation
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1000);
        });
    });
    
    // Swipe gestures for mobile navigation
    if ('ontouchstart' in window) {
        let startX = null;
        let startY = null;
        
        document.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchmove', function(e) {
            if (!startX || !startY) return;
            
            const diffX = startX - e.touches[0].clientX;
            const diffY = startY - e.touches[0].clientY;
            
            // Horizontal swipe detection
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe left - next section
                    navigateToNext();
                } else {
                    // Swipe right - previous section
                    navigateToPrevious();
                }
                
                startX = null;
                startY = null;
            }
        });
    }
}

/**
 * Photo preview and upload enhancements
 */
function setupPhotoPreview() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        if (input.accept && input.accept.includes('image')) {
            input.addEventListener('change', function(e) {
                const files = e.target.files;
                if (files.length > 0) {
                    previewImage(files[0], input);
                }
            });
            
            // Drag and drop support
            const wrapper = input.parentElement;
            if (wrapper) {
                setupDragAndDrop(wrapper, input);
            }
        }
    });
}

function previewImage(file, input) {
    const reader = new FileReader();
    reader.onload = function(e) {
        // Create or update preview
        let preview = input.parentElement.querySelector('.image-preview');
        if (!preview) {
            preview = document.createElement('div');
            preview.className = 'image-preview';
            input.parentElement.appendChild(preview);
        }
        
        preview.innerHTML = `
            <img src="${e.target.result}" alt="预览" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 10px;">
            <p style="color: var(--family-text-secondary); font-size: 0.9rem; margin-top: 5px;">${file.name}</p>
        `;
    };
    reader.readAsDataURL(file);
}

function setupDragAndDrop(wrapper, input) {
    wrapper.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });
    
    wrapper.addEventListener('dragleave', function() {
        this.classList.remove('drag-over');
    });
    
    wrapper.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
            previewImage(files[0], input);
        }
    });
}

/**
 * Form enhancements and smart interactions
 */
function setupFormEnhancements() {
    // Auto-save drafts for long forms
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        if (textarea.name) {
            // Load saved draft
            const savedDraft = localStorage.getItem(`draft_${textarea.name}`);
            if (savedDraft && !textarea.value) {
                textarea.value = savedDraft;
                showDraftNotification(textarea);
            }
            
            // Save drafts on input
            textarea.addEventListener('input', debounce(function() {
                localStorage.setItem(`draft_${textarea.name}`, textarea.value);
            }, 2000));
        }
    });
    
    // Smart form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Clear drafts on successful submit
            const textareas = form.querySelectorAll('textarea');
            textareas.forEach(textarea => {
                if (textarea.name) {
                    localStorage.removeItem(`draft_${textarea.name}`);
                }
            });
        });
    });
    
    // Enhanced date inputs for mobile
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Add quick date options
        const quickDates = document.createElement('div');
        quickDates.className = 'quick-dates';
        quickDates.innerHTML = `
            <button type="button" onclick="setQuickDate(this, 'today')">今天</button>
            <button type="button" onclick="setQuickDate(this, 'yesterday')">昨天</button>
            <button type="button" onclick="setQuickDate(this, 'week')">一周前</button>
        `;
        input.parentElement.appendChild(quickDates);
    });
}

/**
 * Load and display family statistics
 */
function loadFamilyStatistics() {
    // This would typically make an AJAX call to get real-time stats
    // For now, we'll add some visual enhancements to existing stats
    
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach((stat, index) => {
        // Animate numbers counting up
        const finalValue = parseInt(stat.textContent) || 0;
        animateNumber(stat, 0, finalValue, 1000 + (index * 200));
    });
}

/**
 * Utility functions
 */
function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * easeOutQuart(progress));
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function setQuickDate(button, type) {
    const input = button.parentElement.previousElementSibling;
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
    }
    
    if (targetDate) {
        input.value = targetDate.toISOString().split('T')[0];
        input.dispatchEvent(new Event('change'));
    }
}

function showDraftNotification(textarea) {
    const notification = document.createElement('div');
    notification.className = 'draft-notification';
    notification.innerHTML = `
        <span>📝 检测到草稿</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    notification.style.cssText = `
        background: var(--family-info);
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-size: 0.9rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    `;
    textarea.parentElement.insertBefore(notification, textarea);
}

function navigateToNext() {
    // Implementation for swipe navigation
    console.log('Navigate to next section');
}

function navigateToPrevious() {
    // Implementation for swipe navigation
    console.log('Navigate to previous section');
}

// Keyboard shortcuts for power users
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 'n':
                e.preventDefault();
                // Quick add story
                window.location.href = '/admin/family/story/add/';
                break;
            case 'p':
                e.preventDefault();
                // Quick add person
                window.location.href = '/admin/family/person/add/';
                break;
            case 'e':
                e.preventDefault();
                // Quick add event
                window.location.href = '/admin/family/event/add/';
                break;
        }
    }
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log(`Family Admin loaded in ${loadTime}ms`);
        }, 0);
    });
}