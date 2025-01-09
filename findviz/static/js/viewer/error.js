class ViewerError {
    /**
     * Create viewer error handler instance
     * @param {string} [defaultTimeout=5000] - Default timeout for error messages in ms
     */
    constructor(defaultTimeout = 5000) {
        this.defaultTimeout = defaultTimeout;
        this.activeTimeouts = new Map(); // Store active timeouts by error div ID
    }

    /**
     * Display error message in specified DOM element
     * @param {string} message - Error message to display
     * @param {HTMLElement} errorDiv - DOM element to display error in
     * @param {Object} [options] - Additional options
     * @param {number} [options.timeout] - Custom timeout in ms
     * @param {boolean} [options.persistent=false] - If true, error won't auto-hide
     * @param {Function} [options.onHide] - Callback to execute when error is hidden
     */
    displayError(message, errorDiv, options = {}) {
        // Clear any existing timeout for this error div
        if (this.activeTimeouts.has(errorDiv.id)) {
            clearTimeout(this.activeTimeouts.get(errorDiv.id));
        }

        // Set error message and display
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';

        // Auto-hide error unless persistent is true
        if (!options.persistent) {
            const timeout = options.timeout || this.defaultTimeout;
            const timeoutId = setTimeout(() => {
                this.clearError(errorDiv, options.relatedElements, options.onHide);
            }, timeout);
            
            this.activeTimeouts.set(errorDiv.id, timeoutId);
        }
    }

    /**
     * Clear error message and cleanup
     * @param {HTMLElement} errorDiv - DOM element containing error
     * @param {Function} [onHide] - Callback to execute after hiding
     */
    clearError(errorDiv, onHide = null) {
        // Clear error message
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';

        // Execute onHide callback if provided
        if (onHide && typeof onHide === 'function') {
            onHide();
        }

        // Clear timeout reference
        this.activeTimeouts.delete(errorDiv.id);
    }

    /**
     * Clear all active errors
     */
    clearAllErrors() {
        this.activeTimeouts.forEach((timeoutId, errorDivId) => {
            const errorDiv = document.getElementById(errorDivId);
            if (errorDiv) {
                this.clearError(errorDiv);
            }
            clearTimeout(timeoutId);
        });
        this.activeTimeouts.clear();
    }
}

export default ViewerError;