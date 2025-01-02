// file.js
import { 
  FILE_UPLOAD_FIELDS,
  FMRI_FILE_TYPES, 
  UPLOAD_ENDPOINTS, 
} from './constants.js';
import UploadErrorHandler from './error.js';

/** 
 * @typedef {import('./types').UploadResponse} UploadResponse
 * @typedef {import('./types').NiftiFiles} NiftiFiles 
 * @typedef {import('./types').GiftiFiles} GiftiFiles
 * @typedef {import('./types').TimeSeriesFile} TimeSeriesFile
 * @typedef {import('./types').TaskDesignFile} TaskDesignFile
 * @typedef {import('./types').UploadFormData} UploadFormData
 */


/**
 * Class for handling file uploads from findviz upload modal. Files 
 * and form information are passed to Flask routes for validation and
 * server-side processing.
 */
class FileUploader {
  /**
   * Construct a FileUpload class with a callback function (uploadComplete)
   * to be executed on successful upload
   * @param {{ (data: object, plotType: string)  }} onUploadComplete 
   */
  constructor(onUploadComplete) {
    // counter variable to generate unique ids for time series switches
    this.tsFileCounter = 0
    // callback function to run after upload completion
    this.onUploadComplete = onUploadComplete;
    // initialize upload error handler
    this.errorHandler = new UploadErrorHandler();
    // Set up form submission listener
    document.getElementById('upload-form').onsubmit = async (event) => {
      // prevent page reload
      event.preventDefault();
      // get active tabe in form submission
      let activeTab = document.querySelector('.nav-pills .active').getAttribute('href'); // Get the active tab
      // Check whether the input is nifti or gifti based on active tab
      let fmriFileType
      if (activeTab == '#nifti') {
        fmriFileType = FMRI_FILE_TYPES.NIFTI;
      }
      else if (activeTab == '#gifti') {
        fmriFileType = FMRI_FILE_TYPES.GIFTI;;
      }
      this.uploadFiles(event, fmriFileType);
    };

    // get error message placeholder
    this.errorMessageDiv = document.getElementById('error-message-upload');

    // Initialize modal listeners
    this.initializeModalListeners();

    // Initialize TR input form listeners
    this.initializeTRFormListeners();
  }

  /**
   * Upload files to server for validation and processing
   * @param {Event} event - Form submission event
   * @param {string} fmriFileType - Type of fMRI files ('nifti' or 'gifti')
   * @returns {Promise<UploadResponse>}
   */

  async uploadFiles(event, fmriFileType) {
    this.errorHandler.showSpinner();

    try {
        const uploadData = this.getFiles();
        uploadData.append('fmri_file_type', fmriFileType);

        const response = await fetch(UPLOAD_ENDPOINTS.FILES, {
            method: 'POST',
            body: uploadData
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('fmri-visualization-container').style.display = 'block';
            this.onUploadComplete(data, fmriFileType);
            $('#upload-modal').modal('hide');
        } else {
            await this.errorHandler.handleServerError(response, fmriFileType);
        }
    } catch (error) {
        console.error('Error during file upload:', error);
        this.errorHandler.showServerErrorModal();
    } finally {
        this.errorHandler.hideSpinner();
    }
  }

  /**
   * Upload scene file and process cached data
   * @param {object} data - Scene file data
   * @returns {Promise<void>}
   */
  async uploadSceneFile(event, data) {
    this.errorHandler.showSpinner();

    try {
        const sceneFile = event.target.files[0];
        const formData = new FormData();
        formData.append('scene_file', sceneFile);

        const response = await fetch(UPLOAD_ENDPOINTS.SCENE, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            this.errorHandler.showSceneErrorModal();
            throw new Error('Failed server processing of uploaded cache');
        }

        const data = await response.json();
        // get data and call callback function
        // assign time series output to data
        if (data.ts_enabled) {
          Object.assign(data, {timeCourses: data.timeseries})
        } else {
          // If no time courses append empty lists
          Object.assign(data, {timeCourses: {ts: [], tsLabels: []}})
        }

        if (data.task_enabled) {
          Object.assign(data, {taskConditions: data.task})
        } else {
          Object.assign(data, {taskConditions: null})
        }
        this.onUploadComplete(data, data.file_type);
        $('#upload-modal').modal('hide');
    } catch (error) {
        console.error('Error during scene file upload:', error);
        this.errorHandler.showServerErrorModal();
    } finally {
        this.errorHandler.hideSpinner();
    }
  }

  /**
   * Add new time series file input fields to the form
   * Creates a new row with file input, header switch, label textarea, and remove button
   */
  addTimeSeriesFile() {
    const container = document.getElementById('time-series-container');
    const filePair = document.createElement('div');

    // increase counter
    this.tsFileCounter += 1
    // create unique id for switch input
    const uniqueID = `${FILE_UPLOAD_FIELDS.TS.HEADER}-${this.tsFileCounter}`;

    filePair.className = 'times-series-file-pair row mb-2';
    filePair.innerHTML = `
      <div class="col-6">
        <span class="d-inline-block text-secondary">Time Series File (.txt, .csv, optional)</span>
        <i class="fa-solid fa-triangle-exclamation ${FILE_UPLOAD_FIELDS.TS.FILE}-error" style="color: #e93407; display: none;"></i>
        <input type="file" class="form-control-file ${FILE_UPLOAD_FIELDS.TS.FILE} pt-2" data-index="${this.tsFileCounter - 1}">
      </div>
      <div class="col-4">
        <div class="custom-control custom-switch">
          <input type="checkbox" class="custom-control-input ${FILE_UPLOAD_FIELDS.TS.HEADER}" id="${uniqueID}">
          <label class="custom-control-label" for="${uniqueID}">Header</label>
          <span class="fa fa-info-circle ml-1 toggle-immediate" data-toggle="tooltip" data-placement="top" title="Does the file have a header (i.e. name) in the first row?" aria-hidden="true"></span>
        </div>
        <textarea class="form-control ${FILE_UPLOAD_FIELDS.TS.LABEL}" placeholder="Label" rows="1"></textarea>
      </div>
      <div class="col-2 mt-4">
        <button type="button" class="remove-time-series btn btn-danger btn-sm">x</button>
      </div>
    `;
    // Append the new file input to the container
    container.appendChild(filePair);

    // Enable the tooltip
    const tooltip = filePair.querySelector('.toggle-immediate');
    $(tooltip).tooltip()
    // Select the file input we just added
    const newFileInput = filePair.querySelector(`.${FILE_UPLOAD_FIELDS.TS.FILE}`);

     // Select the header switch we just added and add the event listener
    const headerSwitch = filePair.querySelector('.custom-control-input');
    const labelTextarea = filePair.querySelector(`.${FILE_UPLOAD_FIELDS.TS.LABEL}`);

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
   * Clear all fMRI file inputs for a specific type
   * @param {string} fmriType - Type of fMRI files to clear ('nifti' or 'gifti')
   */
  clearfMRIFiles(fmriType) {
    // Get nifti files
    if (fmriType == FMRI_FILE_TYPES.NIFTI) {
      document.getElementById(FILE_UPLOAD_FIELDS.FMRI.NIFTI.FUNC).value = '';
      document.getElementById(FILE_UPLOAD_FIELDS.FMRI.NIFTI.ANAT).value = '';
      document.getElementById(FILE_UPLOAD_FIELDS.FMRI.NIFTI.MASK).value = '';
    // remove gifti files
    } else if (fmriType == FMRI_FILE_TYPES.GIFTI) {
      document.getElementById(FILE_UPLOAD_FIELDS.FMRI.GIFTI.LEFT_FUNC).value = '';
      document.getElementById(FILE_UPLOAD_FIELDS.FMRI.GIFTI.RIGHT_FUNC).value = '';
      document.getElementById(FILE_UPLOAD_FIELDS.FMRI.GIFTI.LEFT_MESH).value = '';
      document.getElementById(FILE_UPLOAD_FIELDS.FMRI.GIFTI.RIGHT_MESH).value = '';
    }
  }

  /**
   * Get NIFTI file inputs and add to form data
   * @returns {FormData & NiftiFiles}
   * @private
  */
    _getNiftiFiles() {
      const formData = new FormData();
      formData.append(
          'nii_func', 
          document.getElementById(FILE_UPLOAD_FIELDS.FMRI.NIFTI.FUNC).files[0]
      );
      formData.append(
          'nii_anat', 
          document.getElementById(FILE_UPLOAD_FIELDS.FMRI.NIFTI.ANAT).files[0]
      );
      formData.append(
          'nii_mask', 
          document.getElementById(FILE_UPLOAD_FIELDS.FMRI.NIFTI.MASK).files[0]
      );
      return formData;
  }

  /**
   * Get GIFTI file inputs and add to form data
   * @returns {FormData & GiftiFiles}
   * @private
   */
  _getGiftiFiles() {
      const formData = new FormData();
      formData.append(
          'left_gii_func', 
          document.getElementById(FILE_UPLOAD_FIELDS.FMRI.GIFTI.LEFT_FUNC).files[0]
      );
      formData.append(
          'right_gii_func',
          document.getElementById(FILE_UPLOAD_FIELDS.FMRI.GIFTI.RIGHT_FUNC).files[0]
      );
      formData.append(
          'left_gii_mesh',
          document.getElementById(FILE_UPLOAD_FIELDS.FMRI.GIFTI.LEFT_MESH).files[0]
      );
      formData.append(
          'right_gii_mesh',
          document.getElementById(FILE_UPLOAD_FIELDS.FMRI.GIFTI.RIGHT_MESH).files[0]
      );
      return formData;
  }

  /**
   * Get time series file inputs and add to form data
   * @returns {{formData: FormData, hasTimeSeries: boolean, files: TimeSeriesFile[]}}
   * @private
   */
  _getTimeSeriesFiles() {
      const formData = new FormData();
      const timeSeriesArray = [];
      const timeSeriesLabelsArray = [];
      const timeSeriesHeaderArray = [];

      const timeSeriesInput = document.querySelectorAll(`.${FILE_UPLOAD_FIELDS.TS.FILE}`);
      const timeSeriesInputLabel = document.querySelectorAll(`.${FILE_UPLOAD_FIELDS.TS.LABEL}`);
      const timeSeriesHeader = document.querySelectorAll(`.${FILE_UPLOAD_FIELDS.TS.HEADER}`);

      for (const [index, ts] of timeSeriesInput.entries()) {
          if (ts.files.length > 0) {
              timeSeriesArray.push(ts.files[0]);
              let tsLabel = timeSeriesInputLabel[index].value || ts.files[0].name;
              timeSeriesLabelsArray.push(tsLabel);
              timeSeriesHeaderArray.push(timeSeriesHeader[index].checked);
          }
      }

      formData.append('ts_files', timeSeriesArray);
      formData.append('ts_labels', timeSeriesLabelsArray);
      formData.append('ts_headers', timeSeriesHeaderArray);

      return {
          formData,
          hasTimeSeries: timeSeriesArray.length > 0
      };
  }

  /**
   * Get task design file inputs and add to form data
   * @returns {{formData: FormData, hasTaskDesign: boolean, taskDesign: TaskDesignFile|null}}
   * @private
   */
  _getTaskDesignFiles() {
      const formData = new FormData();
      const taskInput = document.getElementById(FILE_UPLOAD_FIELDS.TASK.FILE).files[0];

      formData.append('task_file', taskInput);
      formData.append(
          'tr', 
          document.getElementById(FILE_UPLOAD_FIELDS.TASK.TR).value
      );
      formData.append(
          'slicetime_ref',
          document.getElementById(FILE_UPLOAD_FIELDS.TASK.SLICETIME).value
      );

      return {
          formData,
          hasTaskDesign: taskInput !== undefined
      };
  }

  /**
   * Get all files and form data from the upload modal
   * @returns {FormData & UploadFormData}
   */
  getFiles() {
    const masterFormData = new FormData();
    
    // Get active tab to determine fMRI file type
    const activeTab = document.querySelector('.nav-pills .active').getAttribute('href');
    const fmriFileType = activeTab === '#nifti' ? FMRI_FILE_TYPES.NIFTI : FMRI_FILE_TYPES.GIFTI;
    
    // Get all file data
    const fmriData = fmriFileType === FMRI_FILE_TYPES.NIFTI 
        ? this._getNiftiFiles() 
        : this._getGiftiFiles();
    const { formData: tsData, hasTimeSeries, files: tsFiles } = this._getTimeSeriesFiles();
    const { formData: taskData, hasTaskDesign, taskDesign } = this._getTaskDesignFiles();

    // Combine all FormData objects
    [fmriData, tsData, taskData].forEach(formData => {
        for (const [key, value] of formData.entries()) {
            masterFormData.append(key, value);
        }
    });

    // Add flags
    masterFormData.append('fmri_file_type', fmriFileType);
    masterFormData.append('ts_input', hasTimeSeries);
    masterFormData.append('task_input', hasTaskDesign);

    return masterFormData;
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
            UPLOAD_ENDPOINTS.HEADER, 
            { method: 'POST', body: formData }
        );

        if (response.ok) {
            const data = await response.json();
            labelTextarea.value = data.header;
        } else {
            await this.errorHandler.handleServerError(response, 'timecourse');
        }
    } catch (error) {
      console.error('Error reading time course file to get header:', error);
      this.errorHandler.showServerErrorModal();
    }
  }

  /**
   * Initialize modal event listeners
   * Sets up listeners for tab switching, scene file upload, and time series file management
   */
  initializeModalListeners() {
    // create reference to self
    const self = this;
    // Clear inputs and error messages on tab switch
    document.querySelectorAll('.nav-pills .nav-link').forEach(tab => {
      tab.addEventListener('click', function () {
        document.getElementById('error-message-upload').style.display = 'none'; // Clear error message on tab switch
        // Get the currently active tab
        let activeTab = document.querySelector('.nav-pills .active').getAttribute('href');
        let fileType
        if (activeTab == '#nifti') {
          fileType = 'nifti';
        }
        else if (activeTab == '#gifti') {
          fileType = 'gifti';
        }
        // Reset only the FMRI inputs (Nifti or Gifti based on active tab)
        self.clearfMRIFiles(fileType);
      });
    });

    // Open file dialog when user clicks upload scene
    const uploadSceneButton = $('#uploadScene');
    const sceneFileDiv = $('#fileScene');
    uploadSceneButton.on('click', () => {
      // open file dialog
      sceneFileDiv.click();
    });

    // on scene file upload pass to flask route
    sceneFileDiv.on('change', (event) => {
      this.uploadSceneFile();
    });

    // Add event listener for bootstrap model close to clear error message
    $('#uploadModal').on('hidden.bs.modal', function (e) {
        document.getElementById('error-message-upload').style.display = 'none';
    });

    // Event listener for add physio file
    let addTSDiv = document.getElementById('add-time-series')
    addTSDiv.addEventListener('click', this.addTimeSeriesFile.bind(this))

    // On document ready add one time series file
    $(document).ready(function() {
        self.addTimeSeriesFile()
    });
  }

  /**
   * Initialize TR form input synchronization
   * Sets up listeners to keep TR values synchronized across different inputs
   */
  initializeTRFormListeners() {
    // Get references to the input fields for TRs
    // TR input field in modal for Task Design File
    const TRInput1 = document.getElementById(FILE_UPLOAD_FIELDS.TASK.TR);
    // TR input field for fmri preprocessing
    const TRInput2 = document.getElementById('filter-tr');
    // TR input field for time course preprocessing
    const TRInput3 = document.getElementById('ts-filter-tr');

    // Function to update all other TR fields
    function synchronizeInput(sourceInput, targetInputs) {
        sourceInput.addEventListener('input', function() {
            targetInputs.forEach(input => {
                input.value = sourceInput.value;
            });
        });
    }
    // Synchronize all TR input fields fields
    synchronizeInput(TRInput1, [TRInput2, TRInput3]);
    synchronizeInput(TRInput2, [TRInput1, TRInput3]);
    synchronizeInput(TRInput3, [TRInput1, TRInput2]);
  }

  /**
   * Remove time series file input row
   * @param {HTMLButtonElement} button - Remove button that was clicked
   */
  // physio file remove
  removeTimeSeriesFile(button) {
    const filePair = button.closest('.times-series-file-pair');
    filePair.remove();
    // decrease file counter
    this.tsFileCounter -= 1
  }

}


export default FileUploader;
