/**
 * Class for handling file upload errors and displaying error messages
 */

import { LogDisplay } from '../log.js';

class UploadErrorHandler {
    /**
     * Create error handler instance
     * @param {string} errorMessageDivId - ID of main error message div
     * @param {string} serverErrorModalId - ID of server error modal
     * @param {string} sceneErrorModalId - ID of scene error modal
     */
    constructor(
        errorMessageDivId,
        serverErrorModalId,
        sceneErrorModalId
    ) {
        this.errorMessageDiv = document.getElementById(errorMessageDivId);
        this.serverErrorModal = $(`#${serverErrorModalId}`);
        this.sceneErrorModal = $(`#${sceneErrorModalId}`);

        // set up log display
        this.logDisplay = new LogDisplay(
            'toggle-error-upload-log-btn',
            'error-upload-log-container',
            'error-upload-log-content',
            'error-upload-log-status',
            'copy-error-upload-log-btn'
        );

        // initialize modal event listeners
        this.initializeModalEvents();
    }

    /** 
     * Clear error message on any change in the upload modal form
    */
    clearErrorMessageOnFormChange() {
        const form = document.getElementById('upload-form');
        form.addEventListener('input', (event) => {
            this.clearErrorMessage();
        });
    }

    /**
     * Display error message in the upload modal
     * @param {string} message - Error message to display
     * @param {HTMLElement[]} [errorIconDivs=null] - Array of error icon elements to show
     * @param {string[]} [fieldDivs=null] - Array of form field divs associated with each icon
     * @param {boolean} [setErrorTimeout=false] - Whether to automatically hide error after timeout
     * @param {number} [timeOut=5000] - Time in ms before error message is hidden
     */
    displayError(
        message, 
        errorIconDivs = null, 
        fieldDivs = null,
        setErrorTimeout = false, 
        timeOut = 5000
    ) {
        if (this.errorMessageDiv) {
            this.errorMessageDiv.textContent = message;
            this.errorMessageDiv.style.display = 'block';
        }

        // Show error icons if provided
        if (errorIconDivs) {
            errorIconDivs.forEach((icon, index) => {
                // display error icon
                if (icon) {
                    icon.style.display = 'inline-block';
                }
                // set up listener to remove error icon on field change (only runs once)
                fieldDivs[index].addEventListener('change', () => {
                    icon.style.display = 'none';
                }, { once: true })
            });
        }

        // Set timeout to hide error message if requested
        if (setErrorTimeout) {
            setTimeout(() => {
                if (errorIconDivs) {
                    this.clearErrorIcons(errorIconDivs)
                };
                this.clearErrorMessage();
            }, timeOut);
        }
    }

    /**
     * Clear error icons by form fields
     * @param {HTMLElement[]} [errorIconDivs] - Array of error icon elements to hide
     */
    clearErrorIcons(errorIconDivs) {
        if (errorIconDivs) {
            errorIconDivs.forEach(icon => {
                if (icon) {
                    icon.style.display = 'none';
                }
            });
        }
    }

    /**
     * Clear error message in footer of upload modal
     */
    clearErrorMessage() {
        if (this.errorMessageDiv) {
            this.errorMessageDiv.style.display = 'none';
        }
    }

    /**
     * Handle server response errors
     * @param {Response} response - Server response object
     * @param {string} fileType - Type of file that caused error
     * @returns {Promise<void>}
     */
    async handleServerError(response, fileType) {
        const data = await response.json();
        
        let errorIconDivs = [];
        let fieldDivs = [];
        if (data.file_type === 'timecourse') {
            // Get timecourse input error icons by index
            for (const field of data.fields) {
                const timeSeriesFields = document.querySelectorAll(`.${field}`);
                const timeSeriesErrorIcons = document.querySelectorAll(`.${field}-error`);
                for (const index of data.index) {
                    errorIconDivs.push(timeSeriesErrorIcons[index]);
                    fieldDivs.push(timeSeriesFields[index]);
                }
            }
        } else {
            // Get error icon divs for each field
            for (const field of data.fields) {
                errorIconDivs.push(document.getElementById(`${field}-error`));
                fieldDivs.push(document.getElementById(`${field}`));
            }
        }
        this.displayError(data.error, errorIconDivs, fieldDivs);
    }

    /**
     * Initialize modal event listeners
     */
    initializeModalEvents() {
        this.logDisplay.logToggleButton.addEventListener('click', () => {
            this.logDisplay.toggleLogDisplay();
        });

        this.logDisplay.copyLogButton.addEventListener('click', () => {
            this.logDisplay.copyLogToClipboard();
        });

        // set clear error message listener on form input change
        this.clearErrorMessageOnFormChange();
    }

    /**
     * Show generic server error modal
     */
    showServerErrorModal() {
        this.serverErrorModal.modal('show');
        // show log container
        this.logDisplay.showLogContainer();
        this.logDisplay.fetchLogs();
    }

    /**
     * Show scene upload error modal
     */
    showSceneErrorModal() {
        this.sceneErrorModal.modal('show');
    }
}

export default UploadErrorHandler;