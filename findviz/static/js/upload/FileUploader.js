// file.js
import { DOM_IDS } from '../constants/DomIds.js';
import { API_ENDPOINTS } from '../constants/APIEndpoints.js';
// file upload components
import CiftiFileManager from './components/CiftiFileManager.js';
import NiftiFileManager from './components/NiftiFileManager.js';
import GiftiFileManager from './components/GiftiFileManager.js';
import TRFormListener from './components/TRFormListener.js';
import TaskDesignFileManager from './components/TaskDesignFileManager.js';
import TimeSeriesFileManager from './components/TimeSeriesFileManager.js';
import UploadScene from './components/UploadScene.js';
// utilities
import UploadErrorHandler from './UploadErrorHandler.js';
import Spinner from '../Spinner.js';


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
		// callback function to run after upload completion
		this.onUploadComplete = onUploadComplete;

		// upload modal
		this.uploadModal = $(`#${DOM_IDS.FILE_UPLOAD.MODAL}`);
		// submit button
		this.submitButton = $(`#${DOM_IDS.FILE_UPLOAD.SUBMIT_BUTTON}`);

		// initialize upload error handler
		this.errorHandler = new UploadErrorHandler(
			DOM_IDS.FILE_UPLOAD.ERROR_MESSAGE,
			DOM_IDS.FILE_UPLOAD.ERROR_MODAL_SERVER,
			DOM_IDS.FILE_UPLOAD.ERROR_MODAL_SCENE
		);

		// initialize spinner
		this.spinner = new Spinner(
			DOM_IDS.FILE_UPLOAD.SPINNERS.OVERLAY, 
			DOM_IDS.FILE_UPLOAD.SPINNERS.WHEEL
		);

		// Initialize nifti file manager
		this.niftiFileManager = new NiftiFileManager(
			DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.FUNC,
			DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.ANAT,
			DOM_IDS.FILE_UPLOAD.FMRI.NIFTI.MASK,
		);

		// Initialize gifti file manager
		this.giftiFileManager = new GiftiFileManager(
			DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.LEFT_FUNC,
			DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.RIGHT_FUNC,
			DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.LEFT_MESH,
			DOM_IDS.FILE_UPLOAD.FMRI.GIFTI.RIGHT_MESH
		)

		// Initialize cifti file manager
		this.ciftiFileManager = new CiftiFileManager(
			DOM_IDS.FILE_UPLOAD.FMRI.CIFTI.DTSERIES,
			DOM_IDS.FILE_UPLOAD.FMRI.CIFTI.LEFT_MESH,
			DOM_IDS.FILE_UPLOAD.FMRI.CIFTI.RIGHT_MESH
		);

		// Initialize time series file manager
		this.timeSeriesFileManager = new TimeSeriesFileManager(
			DOM_IDS.FILE_UPLOAD.TS.CONTAINER,
			DOM_IDS.FILE_UPLOAD.TS.FILE,
			DOM_IDS.FILE_UPLOAD.TS.HEADER,
			DOM_IDS.FILE_UPLOAD.TS.LABEL,
			DOM_IDS.FILE_UPLOAD.TS.REMOVE_BUTTON,
			DOM_IDS.FILE_UPLOAD.TS.FILE_PAIR,
			DOM_IDS.FILE_UPLOAD.TS.ADD_TS,
			this.errorHandler
		);
		// On document ready add one time series file
		$(document).ready(() => {
			this.timeSeriesFileManager.addTimeSeriesFile()
		});

		// Initialize task design file manager
		this.taskDesignFileManager = new TaskDesignFileManager(
			DOM_IDS.FILE_UPLOAD.TASK.FILE,
			DOM_IDS.FILE_UPLOAD.TASK.TR,
			DOM_IDS.FILE_UPLOAD.TASK.SLICETIME
		);

		// Initialize scene file uploader
		this.sceneFileUploader = new UploadScene(
			DOM_IDS.FILE_UPLOAD.SCENE.BUTTON,
			DOM_IDS.FILE_UPLOAD.SCENE.FILE,
			this.spinner,
			this.errorHandler
		);

		// Initialize TR input form listeners
		this.TRFormListener = new TRFormListener(
			DOM_IDS.FILE_UPLOAD.TASK.TR,
			DOM_IDS.FMRI.PREPROCESSING_OPTIONS.FILTER_TR,
			DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.FILTER_TR,
			DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TR_CONVERT_FORM
		);
		this.TRFormListener.synchronize();

		// Initialize modal listeners
		this.initializeModalListeners();
	}

	/**
	 * Upload files to server for validation and processing
	 * @param {Event} event - Form submission event
	 * @param {string} fmriFileType - Type of fMRI files ('nifti' or 'gifti')
	 * @returns {Promise<void>}
	 */
	async uploadFiles(event, fmriFileType) {
		// show spinner
		this.spinner.show();
		try {
			// get all files and form data
			const uploadData = this.getFiles();
			// append fmri file type to form data
			uploadData.append('fmri_file_type', fmriFileType);
			// send form data to server
			const response = await fetch(API_ENDPOINTS.UPLOAD.FILES, {
				method: 'POST',
				body: uploadData
			});
			// check if server processed files successfully
			if (response.ok) {
				// get data from server
				const data = await response.json();
				// display parent visualization container
				document.getElementById(DOM_IDS.FMRI.VISUALIZATION_CONTAINER).style.display = 'block';
				// call callback function
				this.onUploadComplete(data.file_type);
				// hide upload modal
				this.uploadModal.modal('hide');
			} else {
				// handle server error
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
			// hide spinner
			this.spinner.hide();
		}
	}

	/**
	 * Upload scene file
	 * @param {Event} event - Scene file data
	 */
	async uploadSceneFile(event) {
		// wait for scene file to be uploaded
		const data = await this.sceneFileUploader.uploadFile(event);
		if (data) {
			// display parent visualization container
			document.getElementById(DOM_IDS.FMRI.VISUALIZATION_CONTAINER).style.display = 'block';
			// call callback function
			this.onUploadComplete(data.file_type);
			// hide upload modal
			this.uploadModal.modal('hide');
		}
	}

	/**
	 * Clear all fMRI file inputs for a specific type
	 * @param {string} fmriType - Type of fMRI files to clear ('nifti' or 'gifti')
	 */
	clearfMRIFiles(fmriType) {
		// remove nifti files
		if (fmriType == 'nifti') {
			this.niftiFileManager.clearFiles();
		// remove gifti files
		} else if (fmriType == 'gifti') {
			this.giftiFileManager.clearFiles();
		// remove cifti files
		} else if (fmriType == 'cifti') {
			this.ciftiFileManager.clearFiles();
		}
	}

	/**
	 * Get all files and form data from the upload modal
	 * @returns {FormData}
	 */
	getFiles() {
		// initialize master form data
		const masterFormData = new FormData();
		// Get nifti file data
		const niftiData = this.niftiFileManager.getFiles();
		// Get gifti file data
		const giftiData = this.giftiFileManager.getFiles();
		// Get cifti file data
		const ciftiData = this.ciftiFileManager.getFiles();
		// Get task design file data
		const taskDesignData = this.taskDesignFileManager.getFiles();
		// Get time series file data
		const tsData = this.timeSeriesFileManager.getFiles();

		// check if any time series files are present in array
		const hasTimeSeries = tsData.files.length > 0;
		// check if task design file is present
		const hasTaskDesign = taskDesignData.task_file !== undefined;

		// Append entries from nifti data
		Object.entries(niftiData).forEach(([key, value]) => {
			masterFormData.append(key, value);
		});

		// Append entries from gifti data
		Object.entries(giftiData).forEach(([key, value]) => {
			masterFormData.append(key, value);
		});

		// Append entries from cifti data
		Object.entries(ciftiData).forEach(([key, value]) => {
			masterFormData.append(key, value);
		});

		// Append entries from task design data
		Object.entries(taskDesignData).forEach(([key, value]) => {
			masterFormData.append(key, value);
		});

		// loop through time seriesfiles, headers, and labels
		tsData.files.forEach((file, index) => {
			masterFormData.append('ts_files', file);
			masterFormData.append('ts_headers', tsData.headers[index]);
			masterFormData.append('ts_labels', tsData.labels[index]);
		});

		// Add flags
		masterFormData.append('ts_input', hasTimeSeries);
		masterFormData.append('task_input', hasTaskDesign);

		return masterFormData;
	}

	/**
	 * Initialize modal event listeners
	 * Sets up listeners for tab switching, scene file upload, and time series file management
	 */
	initializeModalListeners() {
		// create reference to self
		const self = this;

		// Set up main form submission listener
		this.submitButton.on('click', async (event) => {
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
			else if (activeTab == '#cifti') {
				fmriFileType = 'cifti';
			}
			this.uploadFiles(event, fmriFileType);
		});
		
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
				else if (activeTab == '#cifti') {
					fileType = 'cifti';
				}
				// Reset only the FMRI inputs (Nifti or Gifti based on active tab)
				self.clearfMRIFiles(fileType);
			});
		});

		// on scene file upload pass to flask route
		const sceneFileDiv = document.getElementById(
			DOM_IDS.FILE_UPLOAD.SCENE.FILE
		);
		sceneFileDiv.addEventListener('change', (event) => {
			this.uploadSceneFile(event);
		});

		// Add event listener for bootstrap model close to clear error message
		this.uploadModal.on('hidden.bs.modal', function () {
			document.getElementById(DOM_IDS.FILE_UPLOAD.ERROR_MESSAGE).style.display = 'none';
		});

		// add a data attribute so Cypress will automatically wait for that attribute to be present
		this.uploadModal.on('shown.bs.modal', (evt) => {
			evt.target.setAttribute('data-cy', 'modal')
		})

		// Remove the `data-cy` attribute when the modal is finished transitioning closed
		this.uploadModal.on('hidden.bs.modal', (evt) => {
			evt.target.removeAttribute('data-cy')
		})
	}

}


export default FileUploader;
