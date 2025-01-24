// error.js
// Error handling for viewer

/**
 * Display error message in modal
 * @param {string} errorMessage - Error message to display
 * @param {string} [modalId='error-viewer-modal'] - ID of error modal
 */
export function displayModalError(errorMessage, modalId = 'error-viewer-modal') {
    // Set error message and display
    const errorDiv = document.getElementById(modalId);
    errorDiv.textContent = errorMessage;
    errorDiv.style.display = 'block';

    // display error modal
    $(`#${modalId}`).modal('show');
}

/**
 * Display error message inline
 * @param {string} errorMessage - Error message to display 
 * @param {string} elementId - ID of inline error element
 */
export function displayInlineError(errorMessage, elementId) {
    // Set error message and display
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
