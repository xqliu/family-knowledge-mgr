/**
 * Rich Text Widget JavaScript
 * Simple rich text editing functionality for story content
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeRichTextWidgets();
});

function initializeRichTextWidgets() {
    const richTextContainers = document.querySelectorAll('.rich-text-container');
    richTextContainers.forEach(container => {
        setupRichTextWidget(container);
    });
}

function setupRichTextWidget(container) {
    const toolbar = container.querySelector('.rich-text-toolbar');
    const textarea = container.querySelector('.rich-text-editor');
    
    if (!toolbar || !textarea) return;
    
    // Setup toolbar button event listeners
    const toolbarBtns = toolbar.querySelectorAll('.toolbar-btn');
    toolbarBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            handleToolbarCommand(this, textarea);
        });
    });
    
    // Setup textarea events
    textarea.addEventListener('keydown', function(e) {
        handleKeyboardShortcuts(e, this);
    });
    
    textarea.addEventListener('input', function() {
        updateToolbarState(toolbar, this);
    });
    
    textarea.addEventListener('selectionchange', function() {
        updateToolbarState(toolbar, this);
    });
    
    // Initial toolbar state
    updateToolbarState(toolbar, textarea);
}

function handleToolbarCommand(button, textarea) {
    const command = button.dataset.command;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    const beforeText = textarea.value.substring(0, start);
    const afterText = textarea.value.substring(end);
    
    let newText = '';
    let newCursorPos = start;
    
    switch(command) {
        case 'bold':
            if (selectedText) {
                newText = `**${selectedText}**`;
                newCursorPos = start + newText.length;
            } else {
                newText = '**粗体文字**';
                newCursorPos = start + 2; // Position cursor after **
            }
            break;
            
        case 'italic':
            if (selectedText) {
                newText = `*${selectedText}*`;
                newCursorPos = start + newText.length;
            } else {
                newText = '*斜体文字*';
                newCursorPos = start + 1; // Position cursor after *
            }
            break;
            
        case 'underline':
            if (selectedText) {
                newText = `<u>${selectedText}</u>`;
                newCursorPos = start + newText.length;
            } else {
                newText = '<u>下划线文字</u>';
                newCursorPos = start + 3; // Position cursor after <u>
            }
            break;
            
        case 'heading':
            const headingText = selectedText || '标题文字';
            newText = `## ${headingText}`;
            newCursorPos = start + newText.length;
            // Add line break if not at start of line
            if (start > 0 && beforeText.charAt(beforeText.length - 1) !== '\n') {
                newText = '\n' + newText;
                newCursorPos += 1;
            }
            if (afterText && afterText.charAt(0) !== '\n') {
                newText += '\n';
            }
            break;
            
        case 'paragraph':
            if (beforeText && beforeText.charAt(beforeText.length - 1) !== '\n') {
                newText = '\n\n';
                newCursorPos = start + 2;
            } else {
                newText = '\n';
                newCursorPos = start + 1;
            }
            break;
            
        case 'quote':
            const quoteText = selectedText || '引用文字';
            newText = `> ${quoteText}`;
            newCursorPos = start + newText.length;
            // Add line break if not at start of line
            if (start > 0 && beforeText.charAt(beforeText.length - 1) !== '\n') {
                newText = '\n' + newText;
                newCursorPos += 1;
            }
            if (afterText && afterText.charAt(0) !== '\n') {
                newText += '\n';
            }
            break;
            
        case 'list':
            const listText = selectedText || '列表项';
            newText = `• ${listText}`;
            newCursorPos = start + newText.length;
            // Add line break if not at start of line
            if (start > 0 && beforeText.charAt(beforeText.length - 1) !== '\n') {
                newText = '\n' + newText;
                newCursorPos += 1;
            }
            if (afterText && afterText.charAt(0) !== '\n') {
                newText += '\n';
            }
            break;
            
        case 'photo':
            newText = '\n[📷 在此插入照片描述]\n';
            newCursorPos = start + newText.length;
            break;
            
        case 'emoji':
            showEmojiPicker(button, textarea, start);
            return; // Don't update text immediately
            
        default:
            return;
    }
    
    // Update textarea content
    textarea.value = beforeText + newText + afterText;
    
    // Set cursor position
    textarea.setSelectionRange(newCursorPos, newCursorPos);
    textarea.focus();
    
    // Trigger input event
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Visual feedback
    button.classList.add('active');
    setTimeout(() => button.classList.remove('active'), 200);
}

function handleKeyboardShortcuts(e, textarea) {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 'b':
                e.preventDefault();
                const boldBtn = textarea.closest('.rich-text-container').querySelector('[data-command="bold"]');
                if (boldBtn) handleToolbarCommand(boldBtn, textarea);
                break;
                
            case 'i':
                e.preventDefault();
                const italicBtn = textarea.closest('.rich-text-container').querySelector('[data-command="italic"]');
                if (italicBtn) handleToolbarCommand(italicBtn, textarea);
                break;
                
            case 'u':
                e.preventDefault();
                const underlineBtn = textarea.closest('.rich-text-container').querySelector('[data-command="underline"]');
                if (underlineBtn) handleToolbarCommand(underlineBtn, textarea);
                break;
        }
    }
    
    // Auto-list continuation
    if (e.key === 'Enter') {
        const cursorPos = textarea.selectionStart;
        const beforeCursor = textarea.value.substring(0, cursorPos);
        const lines = beforeCursor.split('\n');
        const currentLine = lines[lines.length - 1];
        
        // Check if current line starts with list marker
        if (currentLine.match(/^[\s]*[•\-\*]\s/)) {
            e.preventDefault();
            const indent = currentLine.match(/^[\s]*/)[0];
            const marker = currentLine.match(/[•\-\*]/)[0];
            const newListItem = `\n${indent}${marker} `;
            
            const afterCursor = textarea.value.substring(cursorPos);
            textarea.value = beforeCursor + newListItem + afterCursor;
            textarea.setSelectionRange(cursorPos + newListItem.length, cursorPos + newListItem.length);
        }
    }
}

function updateToolbarState(toolbar, textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    // Update button states based on current selection
    const buttons = toolbar.querySelectorAll('.toolbar-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Check if selection contains formatting
    if (selectedText.includes('**')) {
        const boldBtn = toolbar.querySelector('[data-command="bold"]');
        if (boldBtn) boldBtn.classList.add('active');
    }
    
    if (selectedText.includes('*') && !selectedText.includes('**')) {
        const italicBtn = toolbar.querySelector('[data-command="italic"]');
        if (italicBtn) italicBtn.classList.add('active');
    }
    
    if (selectedText.includes('<u>')) {
        const underlineBtn = toolbar.querySelector('[data-command="underline"]');
        if (underlineBtn) underlineBtn.classList.add('active');
    }
}

function showEmojiPicker(button, textarea, cursorPos) {
    // Simple emoji picker
    const emojis = ['😊', '😍', '🥰', '😘', '😁', '😄', '😃', '🤗', '🤔', '😌', '🙏', '👍', '👏', '❤️', '💕', '🎉', '🎊', '🌟', '⭐', '🔥'];
    
    // Create emoji picker popup
    const picker = document.createElement('div');
    picker.className = 'emoji-picker';
    picker.style.cssText = `
        position: absolute;
        background: white;
        border: 1px solid var(--family-border);
        border-radius: var(--radius-md);
        padding: var(--spacing-sm);
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: var(--spacing-xs);
        max-width: 200px;
    `;
    
    emojis.forEach(emoji => {
        const emojiBtn = document.createElement('button');
        emojiBtn.type = 'button';
        emojiBtn.textContent = emoji;
        emojiBtn.style.cssText = `
            border: none;
            background: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: var(--spacing-xs);
            border-radius: var(--radius-sm);
            transition: var(--transition-fast);
        `;
        
        emojiBtn.addEventListener('mouseover', function() {
            this.style.background = 'var(--family-bg)';
        });
        
        emojiBtn.addEventListener('mouseout', function() {
            this.style.background = 'none';
        });
        
        emojiBtn.addEventListener('click', function() {
            insertEmoji(textarea, cursorPos, emoji);
            picker.remove();
        });
        
        picker.appendChild(emojiBtn);
    });
    
    // Position picker near button
    const rect = button.getBoundingClientRect();
    picker.style.top = (rect.bottom + window.scrollY + 5) + 'px';
    picker.style.left = rect.left + 'px';
    
    document.body.appendChild(picker);
    
    // Close picker when clicking outside
    setTimeout(() => {
        const closeHandler = (e) => {
            if (!picker.contains(e.target)) {
                picker.remove();
                document.removeEventListener('click', closeHandler);
            }
        };
        document.addEventListener('click', closeHandler);
    }, 100);
}

function insertEmoji(textarea, cursorPos, emoji) {
    const beforeText = textarea.value.substring(0, cursorPos);
    const afterText = textarea.value.substring(cursorPos);
    
    textarea.value = beforeText + emoji + afterText;
    textarea.setSelectionRange(cursorPos + emoji.length, cursorPos + emoji.length);
    textarea.focus();
    
    // Trigger input event
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
}

// Initialize on dynamic content load
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    const containers = node.querySelectorAll ? node.querySelectorAll('.rich-text-container') : [];
                    containers.forEach(container => {
                        if (!container.dataset.initialized) {
                            setupRichTextWidget(container);
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
    document.addEventListener('DOMContentLoaded', initializeRichTextWidgets);
} else {
    initializeRichTextWidgets();
}