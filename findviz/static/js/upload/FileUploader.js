// file.js
import { DOM_IDS } from '../constants/DomIds.js';
import { API_ENDPOINTS } from '../constants/APIEndpoints.js';
import UploadErrorHandler from './UploadErrorHandler.js';
import Spinner from '../Spinner.js';

/** 
 * @typedef {import('./types.js').UploadResponse} UploadResponse
 * @typedef {import('./types.js').NiftiFiles} NiftiFiles 
 * @typedef {import('./types.js').GiftiFiles} GiftiFiles
 * @typedef {import('./types.js').TimeSeriesFile} TimeSeriesFile
 * @typedef {import('./types.js').TaskDesignFile} TaskDesignFile
 * @typedef {import('./types.js').UploadFormData} UploadFormData
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
   * @param {{ (fileType: string)  }} onUploadComplete 
   */
  constructor(onUploadComplete) {
    // counter variable to generate unique ids for time series switches
    this.tsFileCounter = 0
    // callback function to run after upload completion
    this.onUploadComplete = onUploadComplete;
    // initialize upload error handler
    this.errorHandler = new UploadErrorHandler(DOM_IDS.FILE_UPLOAD.ERROR_MESSAGE);
    // Set up form submission listener
    document.getElementById('upload-form').onsubmit = async (event) => {
      // prevent page reload
      event.preventDefault();
      // get active tabe in form submission
      let activeTab = document.querySelector('.nav-pills .active').getAttribute('href'); // Get the active tab
      // Check whether the input is nifti or gifti based on active tab
      let fmriFileType
      if (activeTab == '#nifti') {
        fmriFileType = 'nifti';
      }
      else if (activeTab == '#gifti') {
        fmriFileType = 'gifti';
      }
      this.uploadFiles(event, fmriFileType);
    };


    // initialize spinner
    this.spinner = new Spinner(
      DOM_IDS.FILE_UPLOAD.SPINNERS.OVERLAY, 
      DOM_IDS.FILE_UPLOAD.SPINNERS.WHEEL
    );

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
    this.spinner.show();

    try {
        const uploadData = this.getFiles();
        uploadData.append('fmri_file_type', fmriFileType);
        const response = await fetch(API_ENDPOINTS.UPLOAD.FILES, {
          method: 'POST',
          body: uploadData
        });
        if (response.ok) {
            const data = await response.json();
            document.getElementById(DOM_IDS.FMRI.VISUALIZATION_CONTAINER).style.display = 'block';
            this.onUploadComplete(data.file_type);
            $('#upload-modal').modal('hide');
        } else {
          if (response.status == 400) {
            console.log('File upload error:', response);
            await this.errorHandler.handleServerError(response, fmriFileType);
          } else {
            console.error('Unexpected error during file upload:', response);
            this.errorHandler.showServerErrorModal();
          }
        }
    } catch (error) {
        console.error('Unexpected error during file upload:', error);
        this.errorHandler.showServerErrorModal();
    } finally {
        this.spinner.hide();
    }
  }

  /**
   * Upload scene file and process cached data
   * @param {object} event - Scene file data
   * @returns {Promise<void>}
   */
  async uploadSceneFile(event) {
    this.spinner.show();

    try {
        const sceneFile = event.target.files[0];
        const formData = new FormData();
        formData.append('scene_file', sceneFile);

        const response = await fetch(API_ENDPOINTS.UPLOAD.SCENE, {
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
        this.onUploadComplete(data.file_type);
        $('#upload-modal').modal('hide');
    } catch (error) {
        console.error('Error during scene file upload:', error);
        this.errorHandler.showServerErrorModal();
    } finally {
        this.spinner.hide();
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
    const uniqueID = `${DOM_IDS.FILE_UPLOAD.TS.HEADER}-${this.tsFileCounter}`;

    filePair.className = 'times-series-file-pair row mb-2';
    filePair.innerHTML = `
      <div class="col-6">
        <span class="d-inline-block text-secondary">Time Series File (.txt, .csv, optional)</span>
        <i class="fa-solid fa-triangle-exclamation ${DOM_IDS.FILE_UPLOAD.TS.FILE}-error" style="color: #e93407; display: none;"></i>
        <input type="file" class="form-control-file ${DOM_IDS.FILE_UPLOAD.TS.FILE} pt-2" data-index="${this.tsFileCounter - 1}">
      </div>
      <div class="col-4">
        <div class="custom-control custom-switch">
          <input type="checkbox" class="custom-control-input ${DOM_IDS.FILE_UPLOAD.TS.HEADER}" id="${uniqueID}">
          <label class="custom-control-label" for="${uniqueID}">Header</label>
          <span class="fa fa-info-circle ml-1 toggle-immediate" data-toggle="tooltip" data-placement="top" title="Does the file have a header (i.e. name) in the first row?" aria-hidden="true"></span>
        </div>
        <textarea class="form-control ${DOM_IDS.FILE_UPLOAD.TS.LABEL}" placeholder="Label" rows="1"></textarea>
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
    const newFileInput = filePair.querySelector(`.${DOM_IDS.FILE_UPLOAD.TS.FILE}`);

     // Select the header switch we just added and add the event listener
    const headerSwitch = filePair.querySelector('.custom-control-input');
    const labelTextarea = filePair.querySelector(`.${DOM_IDS.FILE_UPLOAD.TS.LABEL}`);

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
    if (fmriType == 'nifti') {
      document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.FUNC).value = '';
      document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.ANAT).value = '';
      document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.MASK).value = '';
    // remove gifti files
    } else if (fmriType == 'gifti') {
      document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.LEFT_FUNC).value = '';
      document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.RIGHT_FUNC).value = '';
      document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.LEFT_MESH).value = '';
      document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.RIGHT_MESH).value = '';
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
          document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.FUNC).files[0]
      );
      formData.append(
          'nii_anat', 
          document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.ANAT).files[0]
      );
      formData.append(
          'nii_mask', 
          document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.MASK).files[0]
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
          document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.LEFT_FUNC).files[0]
      );
      formData.append(
          'right_gii_func',
          document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.RIGHT_FUNC).files[0]
      );
      formData.append(
          'left_gii_mesh',
          document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.LEFT_MESH).files[0]
      );
      formData.append(
          'right_gii_mesh',
          document.getElementById(DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.RIGHT_MESH).files[0]
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
      let hasTimeSeries = false;
      const timeSeriesInput = document.querySelectorAll(`.${DOM_IDS.FILE_UPLOAD.TS.FILE}`);
      const timeSeriesInputLabel = document.querySelectorAll(`.${DOM_IDS.FILE_UPLOAD.TS.LABEL}`);
      const timeSeriesHeader = document.querySelectorAll(`.${DOM_IDS.FILE_UPLOAD.TS.HEADER}`);

      for (const [index, ts] of timeSeriesInput.entries()) {
          if (ts.files.length > 0) {
              formData.append('ts_files', ts.files[0]);
              hasTimeSeries = true;
              let tsLabel = timeSeriesInputLabel[index].value || ts.files[0].name;
              formData.append('ts_labels', tsLabel);
              formData.append('ts_headers', timeSeriesHeader[index].checked);
          }
      }
      return {
          formData,
          hasTimeSeries: hasTimeSeries
      };
  }

  /**
   * Get task design file inputs and add to form data
   * @returns {{formData: FormData, hasTaskDesign: boolean, taskDesign: TaskDesignFile|null}}
   * @private
   */
  _getTaskDesignFiles() {
      const formData = new FormData();
      const taskInput = document.getElementById(DOM_IDS.FILE_UPLOAD.TASK.FILE).files[0];

      formData.append('task_file', taskInput);
      formData.append(
          'tr', 
          document.getElementById(DOM_IDS.FILE_UPLOAD.TASK.TR).value
      );
      formData.append(
          'slicetime_ref',
          document.getElementById(DOM_IDS.FILE_UPLOAD.TASK.SLICETIME).value
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
    const fmriFileType = activeTab === '#nifti' ? 'nifti' : 'gifti';
    
    // Get all file data
    const fmriData = fmriFileType === 'nifti' 
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
   * Initialize modal event listeners
   * Sets up listeners for tab switching, scene file upload, and time series file management
   */
  initializeModalListeners() {
    // create reference to self
    const self = this;
    // Clear inputs and error messages on tab switch
    document.querySelectorAll('.nav-pills .nav-link').forEach(tab => {
      tab.addEventListener('click', function () {
        document.getElementById(DOM_IDS.FILE_UPLOAD.ERROR_MESSAGE).style.display = 'none'; // Clear error message on tab switch
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
    $('#upload-modal').on('hidden.bs.modal', function (e) {
        document.getElementById(DOM_IDS.FILE_UPLOAD.ERROR_MESSAGE).style.display = 'none';
    });

    // Event listener for add physio file
    let addTSDiv = document.getElementById(DOM_IDS.FILE_UPLOAD.ADD_TS)
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
    const TRInput1 = document.getElementById(DOM_IDS.FILE_UPLOAD.TASK.TR);
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
