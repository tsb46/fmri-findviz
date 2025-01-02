// 

/**
 * File Upload Response from 
 * @typedef {Object} UploadResponse
 * @property {boolean} success
 * @property {Object} [data]
 */

/**
 * @typedef {Object} NiftiFiles
 * @property {File} nii_func - Functional NIFTI file
 * @property {File} [nii_anat] - Optional anatomical NIFTI file
 * @property {File} [nii_mask] - Optional brain mask NIFTI file
 */

/**
 * @typedef {Object} GiftiFiles
 * @property {File} left_gii_func - Left hemisphere functional GIFTI file
 * @property {File} right_gii_func - Right hemisphere functional GIFTI file
 * @property {File} left_gii_mesh - Left hemisphere mesh GIFTI file
 * @property {File} right_gii_mesh - Right hemisphere mesh GIFTI file
 */

/**
 * @typedef {Object} TimeSeriesFile
 * @property {File} file - Time series data file
 * @property {string} label - Label for the time series
 * @property {boolean} hasHeader - Whether the file has a header
 */

/**
 * @typedef {Object} TaskDesignFile
 * @property {File} file - Task design file
 * @property {number} tr - Repetition time
 * @property {number} slicetimeRef - Slice timing reference (0-1)
 */

/**
 * @typedef {Object} UploadFormData
 * @property {NiftiFiles|GiftiFiles} fmriFiles - FMRI files (either NIFTI or GIFTI)
 * @property {string} fmri_file_type - Type of FMRI files ('nifti' or 'gifti')
 * @property {TimeSeriesFile[]} [timeSeriesFiles] - Optional array of time series files
 * @property {TaskDesignFile} [taskDesign] - Optional task design file and parameters
 * @property {boolean} ts_input - Whether time series files are included
 * @property {boolean} task_input - Whether task design file is included
 */

export {};