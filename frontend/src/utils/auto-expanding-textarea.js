/**
 * FIA v3.0 - Auto-Expanding Textarea Utility
 * Handles automatic textarea resizing (1-3 lines max)
 */

export class AutoExpandingTextarea {
    /**
     * Setup auto-expanding functionality for a textarea
     * @param {HTMLTextAreaElement} textarea - The textarea element to enhance
     * @param {number} maxLines - Maximum number of lines (default: 3)
     */
    static setup(textarea, maxLines = 3) {
        if (!textarea) {
            console.warn('📝 [TEXTAREA] No textarea provided for auto-expanding setup');
            return;
        }
        
        const autoResize = () => {
            // Reset height to auto to get the correct scrollHeight
            textarea.style.height = 'auto';
            
            // Calculate new height (max lines configurable)
            const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight);
            const padding = parseFloat(getComputedStyle(textarea).paddingTop) + 
                           parseFloat(getComputedStyle(textarea).paddingBottom);
            const border = parseFloat(getComputedStyle(textarea).borderTopWidth) + 
                          parseFloat(getComputedStyle(textarea).borderBottomWidth);
            
            const minHeight = lineHeight + padding + border; // 1 line
            const maxHeight = (lineHeight * maxLines) + padding + border; // max lines
            
            let newHeight = Math.min(textarea.scrollHeight, maxHeight);
            newHeight = Math.max(newHeight, minHeight);
            
            textarea.style.height = newHeight + 'px';
            
            // Enable/disable scrolling based on content
            textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
        };
        
        // Auto-resize on input
        textarea.addEventListener('input', autoResize);
        
        // Auto-resize on paste
        textarea.addEventListener('paste', () => {
            setTimeout(autoResize, 0);
        });
        
        // Initial resize
        autoResize();
        
        console.log(`📝 [TEXTAREA] Auto-expanding setup complete (max ${maxLines} lines)`);
        
        // Return cleanup function
        return () => {
            textarea.removeEventListener('input', autoResize);
            textarea.removeEventListener('paste', autoResize);
        };
    }

    /**
     * Reset textarea to single line
     * @param {HTMLTextAreaElement} textarea - The textarea to reset
     */
    static reset(textarea) {
        if (!textarea) return;
        
        textarea.value = '';
        textarea.style.height = 'auto';
        textarea.style.overflowY = 'hidden';
        
        // Trigger resize to single line
        textarea.dispatchEvent(new Event('input'));
    }

    /**
     * Set textarea value and resize appropriately
     * @param {HTMLTextAreaElement} textarea - The textarea
     * @param {string} value - The value to set
     */
    static setValue(textarea, value) {
        if (!textarea) return;
        
        textarea.value = value;
        textarea.dispatchEvent(new Event('input')); // Trigger auto-resize
    }
}