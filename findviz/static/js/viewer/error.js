// error.js
// Error handling for viewer

import { LogDisplay } from '../log.js';

export class ErrorHandler {
    constructor(
        modalId = 'error-viewer-modal',
        modalTextId = 'error-viewer-modal-message'
    ) {
        this.modalId = modalId;
        this.modalTextId = modalTextId;
        this.logDisplay = new LogDisplay(
            'toggle-error-viewer-log-btn',
            'error-viewer-log-container',
            'error-viewer-log-content',
            'error-viewer-log-status',
            'copy-error-viewer-log-btn'
        );
        this.activeErrors = [];
        this.contextId = null;
        
        // Get DOM elements
        this.errorDiv = document.getElementById(modalId);
        this.errorTextDiv = document.getElementById(modalTextId);
        
        // Bind modal events
        this.initializeModalEvents();
    }

    /**
     * Initialize modal event listeners
     */
    initializeModalEvents() {
        $(`#${this.modalId}`).on('hidden.bs.modal', () => {
            this.clearErrors();
            this.logDisplay.hideLogContainer();
        });

        // Add log toggle button event listener
        this.logDisplay.logToggleButton.addEventListener('click', () => {
            this.logDisplay.toggleLogDisplay();
        });

        // Add copy log button event listener
        this.logDisplay.copyLogButton.addEventListener('click', () => {
            this.logDisplay.copyLogToClipboard();
        });
    }

    /**
     * Display error message in modal
     * @param {string} errorMessage - Error message to display
     * @param {string} contextId - Optional context ID for fetching relevant logs
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
        
        // Clear any existing log data
        this.logDisplay.logData = [];
        
        // Automatically show logs
        this.logDisplay.showLogContainer();
        this.logDisplay.fetchLogs();
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

