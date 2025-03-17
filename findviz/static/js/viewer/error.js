// error.js
// Error handling for viewer

export class ErrorHandler {
    constructor(
        modalId = 'error-viewer-modal',
        modalTextId = 'error-viewer-modal-message'
    ) {
        this.modalId = modalId;
        this.modalTextId = modalTextId;
        this.activeErrors = [];
        
        // Get DOM elements
        this.errorDiv = document.getElementById(modalId);
        this.errorTextDiv = document.getElementById(modalTextId);
        
        // Bind modal close event
        this.initializeModalEvents();
    }

    /**
     * Initialize modal event listeners
     */
    initializeModalEvents() {
        $(`#${this.modalId}`).on('hidden.bs.modal', () => {
            this.clearErrors();
        });
    }

    /**
     * Display error message in modal
     * @param {string} errorMessage - Error message to display
     */
    displayError(errorMessage) {
        // Add new error to active errors
        this.activeErrors.push(errorMessage);
        
        // Format all active errors
        const formattedErrors = this.activeErrors
            .map(msg => `• ${msg}`)
            .join('<br>');
        
        // Update error text and show modal
        this.errorTextDiv.innerHTML = formattedErrors;
        this.errorDiv.style.display = 'block';
        $(`#${this.modalId}`).modal('show');
    }

    /**
     * Clear all errors and hide modal
     */
    clearErrors() {
        this.activeErrors = [];
        this.errorTextDiv.innerHTML = '';
        $(`#${this.modalId}`).modal('hide');
    }

    /**
     * Get current number of active errors
     * @returns {number} Number of active errors
     */
    getErrorCount() {
        return this.activeErrors.length;
    }
}

/**
 * Display error message inline
 * @param {string} errorMessage - Error message to display 
 * @param {string} elementId - ID of inline error element
 */
export function displayInlineError(errorMessage, elementId) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.textContent = errorMessage;
    errorDiv.style.display = 'block';
}

/**
 * Clear error message inline
 * @param {string} elementId - ID of inline error element
 */
export function clearInlineError(elementId) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.textContent = '';
    errorDiv.style.display = 'none';
}

// Create and export a singleton instance
export const modalErrorHandler = new ErrorHandler();

