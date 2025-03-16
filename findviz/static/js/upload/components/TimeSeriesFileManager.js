// TimeSeriesFileManager.js
// Manages the time series file DOM elements
import { API_ENDPOINTS } from '../../constants/APIEndpoints.js';
import UploadErrorHandler from '../UploadErrorHandler.js';

class TimeSeriesFileManager {
    /**
     * @param {string} timeSeriesFileContainerId - The ID of the time series file container
     * @param {string} timeSeriesFileInputId - The ID of the time series file input
     * @param {string} timeSeriesFileHeaderId - The ID of the time series file header
     * @param {string} timeSeriesFileLabelId - The ID of the time series file label
     * @param {string} timeSeriesFileRemoveButtonId - The ID of the time series file remove button
     * @param {UploadErrorHandler} errorHandler - The error handler
     */
    constructor(
        timeSeriesFileContainerId,
        timeSeriesFileInputId,
        timeSeriesFileHeaderId,
        timeSeriesFileLabelId,
        timeSeriesFileRemoveButtonId,
        timeSeriesFilePairId,
        timeSeriesAddFileButtonId,
        errorHandler
    ) {
        this.timeSeriesFileContainerId = timeSeriesFileContainerId;
        this.timeSeriesFileInputId = timeSeriesFileInputId;
        this.timeSeriesFileHeaderId = timeSeriesFileHeaderId;
        this.timeSeriesFileLabelId = timeSeriesFileLabelId;
        this.timeSeriesFileRemoveButtonId = timeSeriesFileRemoveButtonId;
        this.timeSeriesFilePairId = timeSeriesFilePairId;
        this.timeSeriesAddFileButtonId = timeSeriesAddFileButtonId;
        this.errorHandler = errorHandler;

        // counter variable to generate unique ids for time series switches
        this.tsFileCounter = 0

        // add event listener to add file button
        const addFileButton = document.getElementById(this.timeSeriesAddFileButtonId);
        addFileButton.addEventListener('click', this.addTimeSeriesFile.bind(this));
    }

    /**
     * Add a new time series file input row
     */
    addTimeSeriesFile() {
        const timeSeriesFileContainer = document.getElementById(this.timeSeriesFileContainerId);
        // create new file pair
        const filePair = document.createElement('div');
        // increase counter
        this.tsFileCounter += 1
        // create unique id for switch input
        const uniqueID = `${this.timeSeriesFileHeaderId}-${this.tsFileCounter}`;
    
        filePair.className = `${this.timeSeriesFilePairId} row mb-2`;
        filePair.innerHTML = `
        <div class="col-6">
            <span class="d-inline-block text-secondary">Time Series File (.txt, .csv, optional)</span>
            <i class="fa-solid fa-triangle-exclamation ${this.timeSeriesFileInputId}-error" style="color: #e93407; display: none;"></i>
            <input type="file" class="form-control-file ${this.timeSeriesFileInputId} pt-2" data-index="${this.tsFileCounter - 1}">
        </div>
        <div class="col-4">
            <div class="custom-control custom-switch">
            <input type="checkbox" class="custom-control-input ${this.timeSeriesFileHeaderId}" id="${uniqueID}">
            <label class="custom-control-label" for="${uniqueID}">Header</label>
            <span class="fa fa-info-circle ml-1 toggle-immediate" data-toggle="tooltip" data-placement="top" title="Does the file have a header (i.e. name) in the first row?" aria-hidden="true"></span>
            </div>
            <textarea class="form-control ${this.timeSeriesFileLabelId}" placeholder="Label" rows="1"></textarea>
        </div>
        <div class="col-2 mt-4">
            <button type="button" class="remove-time-series btn btn-danger btn-sm">x</button>
        </div>
        `;
        // Append the new file input to the container
        timeSeriesFileContainer.appendChild(filePair);

        // Enable the tooltip
        const tooltip = filePair.querySelector('.toggle-immediate');
        $(tooltip).tooltip()
        // Select the file input we just added
        const newFileInput = filePair.querySelector(`.${this.timeSeriesFileInputId}`);

        // get the header switch we just added and add the event listener
        const headerSwitch = filePair.querySelector('.custom-control-input');
        const labelTextarea = filePair.querySelector(`.${this.timeSeriesFileLabelId}`);

        headerSwitch.addEventListener('change', () => {
            if (headerSwitch.checked) {
                const newFileIndex = newFileInput.dataset.index;
                this.handleHeaderSwitch(newFileInput, labelTextarea, newFileIndex);
            } else {
                // Clear label if switch is toggled off
                labelTextarea.value = '';
            }
        });

        // Select the remove button we just added and add the event listener
        const removeButton = filePair.querySelector('button');
        removeButton.addEventListener('click', () => {
            this.removeTimeSeriesFile(removeButton);
        });
    }

    /**
	 * Get time series file inputs
	 * @returns {{files: object[], labels: object[], headers: object[]}}
	 */
	getFiles() {
		const files = [];
		const labels = [];
		const headers = [];
        // get all time series file inputs
		const timeSeriesInput = document.querySelectorAll(`.${this.timeSeriesFileInputId}`);
        // get all time series file labels
		const timeSeriesInputLabel = document.querySelectorAll(`.${this.timeSeriesFileLabelId}`);
        // get all time series file headers
		const timeSeriesHeader = document.querySelectorAll(`.${this.timeSeriesFileHeaderId}`);

		for (const [index, ts] of timeSeriesInput.entries()) {
            if (ts.files.length > 0) {
                files.push(ts.files[0]);
                let tsLabel = timeSeriesInputLabel[index].value || ts.files[0].name;
                labels.push(tsLabel);
                headers.push(timeSeriesHeader[index].checked);
            }
        }
		return {
				files,
				labels,
				headers
		};
	}

    /**
     * Handle header switch toggle for time series files
     * Fetches and displays header from file when switch is toggled on
     * @param {HTMLInputElement} fileInput - File input element
     * @param {HTMLTextAreaElement} labelTextarea - Label textarea element
     * @param {number} fileIndex - index of file input
     * @returns {Promise<void>}
     */
    async handleHeaderSwitch(fileInput, labelTextarea, fileIndex) {
        if (!fileInput.files.length) {
            this.errorHandler.displayError('Please select a file before enabling header');
            return;
        }

        const formData = new FormData();
        formData.append('ts_file', fileInput.files[0]);
        formData.append('file_index', fileIndex);

        try {
            const response = await fetch(
                API_ENDPOINTS.UPLOAD.HEADER, 
                { method: 'POST', body: formData }
            );

            if (response.ok) {
                const data = await response.json();
                labelTextarea.value = data.header;
            } else {
                if (response.status == 400) {
                    console.log('Header error:', response);
                    await this.errorHandler.handleServerError(response, 'timecourse');
                } else {
                    console.error('Unexpected error during header fetch:', response);
                    this.errorHandler.showServerErrorModal();
                }
            }
        } catch (error) {
            console.error('Unexpected error during header fetch:', error);
            this.errorHandler.showServerErrorModal();
        }
    }

    /**
     * Remove time series file input row
     * @param {HTMLButtonElement} button - Remove button that was clicked
     */
    removeTimeSeriesFile(button) {
        const filePair = button.closest('.times-series-file-pair');
        filePair.remove();
        // decrease file counter
        this.tsFileCounter -= 1
    }
}

export default TimeSeriesFileManager;